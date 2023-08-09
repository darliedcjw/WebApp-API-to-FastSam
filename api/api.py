import io
import ast
import re
import base64
import torch
from datetime import datetime
from flask import Flask, jsonify, request
from PIL import Image
from pydantic import BaseModel, field_validator
from typing import Dict, Any
from FastSAM.fastsam import FastSAM, FastSAMPrompt

app = Flask(__name__)


app.config['APP RESULT'] = 'http://localhost:5000/result'


# Load Model
weights_path = 'FastSAM/weights/FastSAM-x.pt'
model = FastSAM(weights_path)
print("Model is hotloaded!")

# Pydantic Class
class InferenceRequestModel(BaseModel):
    files : Dict[str, Any] # TODO establish what the data type of the binary file will be
    data : Dict[str, str]

    # validating that the files parameter does contain data
    @field_validator('files')
    @classmethod
    def file_must_contain_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        value = v['image']
        if value is None or value == '':
            raise ValueError("Image must contain data")
        return v

    # validating that the mode was correctly input
    @field_validator('data')
    @classmethod
    def data_must_contain_mode(cls, v: Dict[str, str]) -> Dict[str, str]:
        if v['mode'].strip() not in ['everything', 'box', 'text', 'points']:
            raise ValueError("Only accept the following mode: ['everything', 'box', 'text', 'points']")
        return v

    # validating that for mode == everything, no other parameters are sent
    @field_validator('data')
    @classmethod
    def mode_everything_data_must_contain_nothing_else(cls, v: Dict[str, str]) -> Dict[str, str]:
        if v['mode'].strip() in 'everything':
            assert 'data' not in v, "Too many parameters provided for mode == 'everything'"
        return v

    # validating that for mode == box, the set of coordinates are received
    @field_validator('data')
    @classmethod
    def mode_box_data_must_contain_box_prompt(cls, v: Dict[str, str]) -> Dict[str, str]:
        if v['mode'].strip() in 'box':
            params = ast.literal_eval(v['data'])
            assert len(params) == 1, "Incorrect number of params in dictionary for mode = 'box'"
            assert 'box_prompt' in params, "box_prompt key is missing from data"
            box_data = params['box_prompt']
            assert box_data and isinstance(box_data, list) and len(box_data) == 1 and all(isinstance(x, float) for x in box_data[0]) and len(box_data[0]) == 4, "box_prompt value does not follow the proper format"
        return v
    
    # validating that for mode == points, the two additional key value pairs are received, containing at least 2 inner lists (in the point_prompt)
    @field_validator('data')
    @classmethod
    def mode_points_data_must_contain_corresponding_fields(cls, v: Dict[str, str]) -> Dict[str, str]:
        if v['mode'].strip() in 'points':
            params = ast.literal_eval(v['data'])
            assert len(params) == 2, "Incorrect number of items in dictionary for mode = 'points'"
            assert 'point_prompt' in params, "point_prompt key is missing from data"
            assert 'point_label' in params, "point_label key is missing from data"
            point_prompt_list = params['point_prompt']
            point_label_list = params['point_label']

            assert isinstance(point_prompt_list, list) and len(point_prompt_list) >= 2 and all(isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, float) for x in pair) for pair in point_prompt_list), "point_prompt value does not follow the proper format"
            assert isinstance(point_label_list, list) and all(isinstance(x, int) for x in point_label_list) and len(point_label_list) == len(point_prompt_list), "point_label value does not follow the proper format"
        return v
    
    # validating that for mode == text, an additional key value pair containing text is received
    @field_validator('data')
    @classmethod
    def mode_text_data_must_contain_string(cls, v: Dict[str, str]) -> Dict[str, str]:
        if v['mode'].strip() in 'text':
            params = ast.literal_eval(v['data'])
            assert len(params) == 1, "Incorrect number of items in dictionary for mode = 'text'"
            assert 'text_prompt' in params, "text_prompt key is missing from data"
            text_prompt = params['text_prompt']

            assert text_prompt.replace(" ", "").isalpha(), "text_prompt does not contain alphabetic data"

        return v    

            
# Ping API endpoint
@app.route("/ping", methods=["GET"])
def ping():
    response = {"message": "pong"}
    return jsonify(response)


# Inference API Endpoint
@app.route('/infer', methods=["POST"])
def infer():

    # Check if information is posted correctly
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 401
    if 'mode' not in request.form:
        return jsonify({'error': 'No mode/data provided.'}), 402


    # Default Parameters
    imgsz = 1024
    iou = 0.9
    conf = 0.4
    output = 'output/'
    output_label = datetime.now().strftime('%Y%m%d_%H%M%S')
    randomcolor = True
    better_quality = False
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    retina = True
    withContours = False
    text_prompt = None
    label = "[0]"
    point_prompt = "[[0,0]]"
    box_prompt = "[[0,0,0,0]]"

    files = {} 
    data = {}
    
    # Image
    files['image'] = request.files['image']
    
    # Data
    data['mode'] = request.form['mode']
    if data['mode'] != 'everything':
        data['data'] = request.form['data']

    # First Check: Using Pydantic
    InferenceRequestModel(files=files, data=data)

    # Image Processing
    image_bytes = bytearray(files['image'].read())
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")

    # Mode: (1) Everything
    if data['mode'] == 'everything':
        # (1.1) Everything Input Check: Empty String
        box_prompt = ast.literal_eval(box_prompt)
        point_prompt = ast.literal_eval(point_prompt)
        label = ast.literal_eval(label)


    # Mode: (2) Box
    elif data['mode'] == 'box':
        # (2.1) Box Input Check: Correct input format
        result = re.search('\{\'|"box_prompt\'|": \[\[\s*0?\.?\d+,\s*0?\.?\d+,\s*0?\.?\d+,\s*0?\.?\d+\s*\]\]\}', data['data'])
        if not result:
            raise ValueError('Data should be: \'{"box_prompt": [[x_top_left,y_top_left,x_bottom_right,y_bottom_right]]}\' for example \[[.0,.4,.7,1]]\. \
                             Please note that floats can be written as (.1, 0.1 e.g.) \
                             and and only the format 1 without decimal is accepted. \
                             Whitespaces should also be strictly followed.')
        
        # (2.2) Box Input Check: Normalisation between (0, 1)
        data = ast.literal_eval(data['data'])
        box_prompt = data['box_prompt']
        assert .0 <= box_prompt[0][0] <= 1.0, "Index 0 should be between .0 and 1.0"
        assert .0 <= box_prompt[0][1] <= 1.0, "Index 1 should be between .0 and 1.0"
        assert .0 <= box_prompt[0][2] <= 1.0, "Index 2 should be between .0 and 1.0"
        assert .0 <= box_prompt[0][3] <= 1.0, "Index 3 should be between .0 and 1.0"
        
        # (2.3.) Rescale bounding box coordinates to orignal size (Else not rescaled for unknown reasons)
        box_prompt[0][0] = image.size[0]*box_prompt[0][0]
        box_prompt[0][1] = image.size[1]*box_prompt[0][1]
        box_prompt[0][2] = image.size[0]*box_prompt[0][2]
        box_prompt[0][3] = image.size[1]*box_prompt[0][3]

        print(box_prompt)
        print(image.size)
        
        point_prompt = ast.literal_eval(point_prompt)
        label = ast.literal_eval(label)

        print(box_prompt)

    # Mode: (3) Text
    elif data['mode'] == 'text':
        # (3.1) Text Input Check: Correct input format (str)
        result = re.search('\{\'|"text_prompt\'|": \'|"[\w\s]*\'|"\}', data['data'])
        if not result:
            raise ValueError('Data should be: \'{"text_prompt": "This is a white cat"}\'. \
                             Input must be in type "str"!')
        
        # (3.2) Text Input Check: Input is not empty string
        data = ast.literal_eval(data['data'])
        text_prompt = data['text_prompt']
        assert text_prompt != "", 'String must not be empty'
        
        box_prompt = ast.literal_eval(box_prompt)
        point_prompt = ast.literal_eval(point_prompt)
        label = ast.literal_eval(label)

    # Mode: (4) Points
    elif data['mode'] == 'points':
        # (4.1) Points Input Check: Correct input format
        result = re.search('\{\'|"point_prompt\'|": \[\[0?\.?\d+\s*,0?\.?\d+\s*\](,\s*\[0?\.?\d+\s*,0?\.?\d+\s*\])*\],\s*\'|"point_label\'|": \[(1|0,\s*)*1|0\s*\]\}', data['data'])
        if not result:
            raise ValueError('Data should be: \'{"point_prompt": [[.3,.5],[.6,.8]]}, {"point_label": [1,0]}\' for example. \
                             Please note that floats can be written as (.1, 0.1 e.g.) \
                             and and only the number 1 without decimal is accepted.')

        data = ast.literal_eval(data['data'])

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


    # Save the mask image
    prompt_process.plot(
        annotations=ann,
        output_path=output + '{}.jpg'.format(output_label),
        bboxes = bboxes,
        points = points,
        point_label = point_label,
        withContours=withContours,
        better_quality=better_quality,
    )


    # Return mask image
    maskImage_path = output + '{}.jpg'.format(output_label)

    with open(maskImage_path, 'rb') as image_file:    
        binary_data = image_file.read()
        base64_data = base64.b64encode(binary_data).decode('utf-8')

        return jsonify({'image': base64_data})

if __name__ == "__main__":
    app.run(port=4000, debug=True)