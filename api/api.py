from datetime import datetime
from flask import Flask, jsonify, request
from PIL import Image
from pydantic import BaseModel, field_validator
import io
import ast
import re


import torch
from FastSAM.fastsam import FastSAM, FastSAMPrompt
from FastSAM.utils.tools import convert_box_xywh_to_xyxy

app = Flask(__name__)


weights_path = 'FastSAM/weights/FastSAM-x.pt'
model = FastSAM(weights_path)
print("Model is hotloaded!")


class InferenceRequest(BaseModel):
    mode : str
    data : str

    @field_validator('mode')
    @classmethod
    def check_mode(cls, v):
        if v not in ['everything', 'box', 'text', 'points']:
            raise ValueError('Only accept the following mode: [\'everything\', \'box\', \'text\', \'points\']')
        return        

            
# Ping API endpoint
@app.route("/ping", methods=["GET", "POST"])
def ping():
    response = {"message": "pong"}
    return jsonify(response)


# Inference API Endpoint
@app.route('/infer', methods=["GET", "POST"])
def infer():

    # Check if information is posted correctly
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 401
    if 'mode' not in request.form or 'data' not in request.form:
        return jsonify({'error': 'No mode/data provided.'}), 402


    # Default Parameters
    imgsz = 1024
    iou = 0.9
    conf = 0.4
    output = 'output/'
    output_label = datetime.now().strftime('%Y%m%d_%H%M%S')
    randomcolor = False
    better_quality = False
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    retina = True
    withContours = False
    text_prompt = None
    label = "[0]"
    point_prompt = "[[0,0]]"
    box_prompt = "[[0,0,0,0]]"

    # Image
    image_file = request.files['image']
    image_bytes = bytearray(image_file.read())
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    
    
    # Data
    validate_data = {}
    mode = request.form['mode']
    data = request.form['data']
    validate_data['mode'] = mode
    validate_data['data'] = data


    # Mode Check: Using Pydantic
    InferenceRequest(**validate_data)


    # Mode: (1) Everything
    if mode == 'everything':
        # (1.1) Everything Input Check: Empty String
        assert data == '', 'Data should be an empty string: for e.g. \'\''
        box_prompt = ast.literal_eval(box_prompt)
        box_prompt = convert_box_xywh_to_xyxy(box_prompt)
        point_prompt = ast.literal_eval(point_prompt)
        label = ast.literal_eval(label)

    # Mode: (2) Box
    elif mode == 'box':
        # (2.1) Box Input Check: Correct input format and top left coordinates (.0,.0)
        result = re.search('\{\'|"box_prompt\'|": \[\[0?\.?\d+\s*,0?\.?\d+\s*,0?\.?\d+\s*,0?\.?\d+\s*\]\]\}', data)
        if not result:
            raise ValueError('Data should be: \'{"box_prompt": [[x_top_left,y_top_left,x_bottom_right,y_bottom_right]]}\' for example \[[.0,.4,.7,1]]\. \
                             Please note that floats can be written as (.1, 0.1 e.g.) \
                             and and only the format 1 without decimal is accepted. \
                             Whitespaces should also be strictly followed.')
        # (2.2) Box Input Check: Normalisation between (0, 1)
        data = ast.literal_eval(data)
        box_prompt = data['box_prompt']
        assert .0 <= box_prompt[0][2] <= 1.0, "Index 2 should be between .0 and 1.0"
        assert .0 <= box_prompt[0][3] <= 1.0, "Index 3 should be between .0 and 1.0"
        
        # (2.3.) Rescale bounding box coordinates to orignal size (Else not rescaled for unknown reasons)
        box_prompt[0][2] = image.size[0]*box_prompt[0][2]
        box_prompt[0][3] = image.size[1]*box_prompt[0][3]

        box_prompt = convert_box_xywh_to_xyxy(box_prompt)
        point_prompt = ast.literal_eval(point_prompt)
        label = ast.literal_eval(label)

    # Mode: (3) Text
    elif mode == 'text':
        # (3.1) Text Input Check: Correct input format (str)
        result = re.search('\{\'|"text_prompt\'|": \'|"[\w\s]*\'|"\}', data)
        if not result:
            raise ValueError('Data should be: \'{"text_prompt": "This is a white cat"}\'. \
                             Input must be in type "str"!')
        # (3.2) Text Input Check: Input is not empty string
        data = ast.literal_eval(data)
        text_prompt = data['text_prompt']
        assert text_prompt != "", 'String must not be empty'
        
        box_prompt = ast.literal_eval(box_prompt)
        box_prompt = convert_box_xywh_to_xyxy(box_prompt)
        point_prompt = ast.literal_eval(point_prompt)
        label = ast.literal_eval(label)

    # Mode: (4) Points
    elif mode == 'points':
        # (4.1) Points Input Check: Correct input format
        result = re.search('\{\'|"point_prompt\'|": \[\[0?\.?\d+\s*,0?\.?\d+\s*\](,\s*\[0?\.?\d+\s*,0?\.?\d+\s*\])*\],\s*\'|"point_label\'|": \[(1|0,\s*)*1|0\s*\]\}', data)
        if not result:
            raise ValueError('Data should be: \'{"point_prompt": [[.3,.5],[.6,.8]]}, {"point_label": [1,0]}\' for example. \
                             Please note that floats can be written as (.1, 0.1 e.g.) \
                             and and only the number 1 without decimal is accepted.')

        data = ast.literal_eval(data)


        # (4.2) Points Input Check: Len(Points) == Len(Label) and Normalisation between (0, 1)
        point_prompt = data['point_prompt']
        label = data['point_label']
        assert len(point_prompt) == len(label), "Length of point_prompt must be equal to length of label."
        for i in range(len(point_prompt)):
            assert .0 <= point_prompt[i][0] <= 1.0, "Point {} of index 0 should be between .0 and 1.0".format(i)
            assert .0 <= point_prompt[i][1] <= 1.0, "Point {} of index 1 should be between .0 and 1.0".format(i)

            # (4.3) Rescale bounding box coordinates to orignal size
            point_prompt[i][0] = int(image.size[0]*point_prompt[i][0]) 
            point_prompt[i][1] = int(image.size[1]*point_prompt[i][1]) 

        box_prompt = ast.literal_eval(box_prompt)
        box_prompt = convert_box_xywh_to_xyxy(box_prompt)
        

    # Prediction
    everything_results = model(
        image, 
        device=device, 
        retina_masks=retina, 
        imgsz=imgsz, 
        conf=conf,
        iou=iou
        )
    
    bboxes = None
    points = None
    point_label = None

    prompt_process = FastSAMPrompt(image, everything_results, device=device)

    if box_prompt[0][2] != 0 and box_prompt[0][3] != 0:
            ann = prompt_process.box_prompt(bboxes=box_prompt)
            bboxes = box_prompt
    elif text_prompt != None:
        ann = prompt_process.text_prompt(text=text_prompt)
    elif point_prompt[0] != [0, 0]:
        ann = prompt_process.point_prompt(
            points=point_prompt, pointlabel=label
        )
        points = point_prompt
        point_label = label
    else:
        ann = prompt_process.everything_prompt()

    prompt_process.plot(
        annotations=ann,
        output_path=output + '{}.jpg'.format(output_label),
        bboxes = bboxes,
        points = points,
        point_label = point_label,
        withContours=withContours,
        better_quality=better_quality,
    )

    return 'Finish'

if __name__ == "__main__":
    app.run(port=4000)