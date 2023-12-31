from flask import Flask, jsonify, request, render_template
from PIL import Image, ImageDraw
import random
import os
import requests
import io
import base64

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'static/images'  # Define the folder to store uploaded images
app.config['API INFER'] = 'http://localhost:4000/infer'


# Make upload folder
if not os.path.exists('static/images'):
    os.mkdir('static/images')


# Home Page
@app.route('/')
def index():
    return render_template('index.html')


# Upload
@app.route('/upload', methods=['POST'])
def upload():
    if 'image' in request.files:
        image = request.files['image']

        if image.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpeg')
            image.save(image_path)
            width, height = Image.open(image).size
            
            return jsonify({'message': 'Image uploaded successfully', 'image_path': image_path, 'width': width, 'height': height})
    

# Preview of Bounding Box
@app.route('/drawBox', methods=['POST'])
def drawBox():
    box_coordinates = request.json.get('box_coordinates')

    if box_coordinates:
        x1 = box_coordinates[0]
        y1 = box_coordinates[1]
        x2 = box_coordinates[2]
        y2 = box_coordinates[3]
        
        image_path = 'static/images/image.jpeg'
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        draw.rectangle([x1, y1, x2, y2], outline='red', width=2)

        new_image_path = 'static/images/modified_image.jpeg'
        image.save(new_image_path)

        return jsonify({'image_path': new_image_path})
    

# Preview of Points
@app.route('/drawPoints', methods=['POST'])
def drawPoints():
    points = request.json.get('points')
    total_points = []
    total_label = []
    color_label = []

    for i in range(len(points)):
        if i%2 == 0:
            # Check points pair input
            assert '' not in points, 'One of the points pair (e.g. points, labels) are missing!'

            total_points.append([int(point) for point in points[i].split(',')])
            total_label.append(int(points[i+1]))

    # Check x,y coordinate pair
    for point in total_points:
        assert len(point) == 2, 'One of the coordinates is missing!'

    # Draw Points using ellipse (Bigger to visualise)
    if total_points and total_label:
        image_path = 'static/images/image.jpeg'
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Specific color for same labels
        for _ in set(total_label):
            color_label.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    
        for i, (x,y) in enumerate(total_points):
            radius = 5
            x1, y1 = x - radius, y - radius           
            x2, y2 = x + radius, y + radius           
            draw.ellipse((x1,y1,x2,y2), fill=color_label[total_label[i] - 1])
            
        new_image_path = 'static/images/modified_image.jpeg'
        image.save(new_image_path)

        return jsonify({'image_path': new_image_path})
    

# Mask Prediction: "everything"
@app.route('/predictEverything', methods=['POST'])
def predictEverything():
    image_path = 'static/images/image.jpeg'

    with open(image_path, 'rb') as image_file:
        files = {'image': image_file}
        data = {'mode': 'everything',
            }
        
        response = requests.post(app.config['API INFER'], files=files, data=data)
        response_json = response.json()

        if response_json.get('image') is not None:
            image_64 = response_json.get('image')
            image_bytes = base64.b64decode(image_64)
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert("RGB")
            new_image_path = 'static/images/modified_image.jpeg'
            image.save(new_image_path)

            return jsonify({'image_path': new_image_path})
        
        else:
            print('API request failed!')


@app.route('/predictBox', methods=['POST'])
def predictBox():
    box_coordinates = request.json.get('box_coordinates')
    
    if box_coordinates:
        image_path = 'static/images/image.jpeg'
        image = Image.open(image_path)
        width, height = image.size

        box_coordinates[0] /= width
        box_coordinates[1] /= height
        box_coordinates[2] /= width
        box_coordinates[3] /= height

        box_params = '{"box_prompt": ' + '[{}]}}'.format(box_coordinates)

        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            data = {'mode': 'box',
                    'data': box_params,
                }
            
            response = requests.post(app.config['API INFER'], files=files, data=data)
            response_json = response.json()

            if response_json.get('image') is not None:
                image_64 = response_json.get('image')
                image_bytes = base64.b64decode(image_64)
                image = Image.open(io.BytesIO(image_bytes))
                image = image.convert("RGB")
                new_image_path = 'static/images/modified_image.jpeg'
                image.save(new_image_path)

                return jsonify({'image_path': new_image_path})
            
            else:
                print('API request failed!')


@app.route('/predictText', methods=['POST'])
def predictText():
    text = request.json.get('text')

    if text:
        image_path = 'static/images/image.jpeg'
        
        text_params = '{"text_prompt": "' + text + '"}'

        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            data = {'mode': 'text',
                    'data': text_params,
                }
            
            response = requests.post(app.config['API INFER'], files=files, data=data)
            response_json = response.json()

            if response_json.get('image') is not None:
                image_64 = response_json.get('image')
                image_bytes = base64.b64decode(image_64)
                image = Image.open(io.BytesIO(image_bytes))
                image = image.convert("RGB")
                new_image_path = 'static/images/modified_image.jpeg'
                image.save(new_image_path)

                return jsonify({'image_path': new_image_path})
            
            else:
                print('API request failed!')


@app.route('/predictPoints', methods=['POST'])
def predictPoints():
    points = request.json.get('points')

    if points:
        image_path = 'static/images/image.jpeg'
        image = Image.open(image_path)
        width, height = image.size
        
        total_points = []
        total_label = []

        # Count the number of fields
        for i in range(len(points)):
            if i%2 == 0:
                # Check points pair input
                assert '' not in points, 'One of the points pair (e.g. points, labels) are missing!'

                total_points.append([int(point) for point in points[i].split(',')])
                total_label.append(int(points[i+1]))

        # Check x,y coordinate pair
        for point in total_points:
            assert len(point) == 2, 'One of the coordinates is missing!'

        for i in range(len(total_points)):
            total_points[i][0] /= width
            total_points[i][1] /= height

        points_params = '{{"point_prompt": {}, "point_label": {}}}'.format(total_points, total_label)

        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            data = {'mode': 'points',
                    'data': points_params,
                }
            
            response = requests.post(app.config['API INFER'], files=files, data=data)
            response_json = response.json()

            if response_json.get('image') is not None:
                image_64 = response_json.get('image')
                image_bytes = base64.b64decode(image_64)
                image = Image.open(io.BytesIO(image_bytes))
                image = image.convert("RGB")
                new_image_path = 'static/images/modified_image.jpeg'
                image.save(new_image_path)

                return jsonify({'image_path': new_image_path})
            
            else:
                print('API request failed!')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)