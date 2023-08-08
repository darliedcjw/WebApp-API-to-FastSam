from datetime import datetime
from flask import Flask, jsonify, request, render_template
from PIL import Image, ImageDraw, ImageFont
import random
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/images'  # Define the folder to store uploaded images

# Make upload folder
if not os.path.exists('static/images'):
    os.mkdir('static/images')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpeg')
            image.save(image_path)
            
            width, height = Image.open(image).size
            
            return jsonify({'message': 'Image uploaded successfully', 'image_path': image_path, 'width': width, 'height': height})
    

@app.route('/drawBox', methods=['POST', 'GET'])
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
    

@app.route('/drawPoints', methods=['POST', 'GET'])
def drawPoints():
    points = request.json.get('points')
    total_points = []
    total_label = []
    color_label = []


    # Count the number of fields
    for i in range(len(points)):
        if i%2 == 0:
            # Check empty: Drop if either point or label is empty
            if points[i] == '' or points[i + 1] == '':
                continue
            else:
                total_points.append([int(point) for point in points[i].split(',')])
                total_label.append(int(points[i+1]))

    # Assert length labels == length points
    assert len(total_points) == len(total_label), 'the number of points is not equal to the number of labels'

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
    
    
@app.route('/predictEverything', methods=['POST', 'GET'])
def predictEverything():
    
    


if __name__ == '__main__':
    app.run(port=4000, debug=True)