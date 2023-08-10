**There are a total of 8 steps**
Frontend is exposed on port:5000
Python Version == "3.11.2"
OS: Windows
Remarks: Please ensure that that api service is running on the docker container. Else, refer to the "API Docker Instructions (ReadMe).txt" first.
==========================================================================================================================================================================================
1. Create a venv (Desktop)
[Command]: py -m venv venv
==========================================================================================================================================================================================
2. Activate venv
[Command]: venv\scripts\activate
==========================================================================================================================================================================================
3. cd to "frontend" folder
==========================================================================================================================================================================================
4. Install libraries and dependencies
[Command]: pip install -r requirements.txt
==========================================================================================================================================================================================
5. Run app
[Command]: py app.py
==========================================================================================================================================================================================
6. Go to Web Application
Link: http://localhost:5000
==========================================================================================================================================================================================
7. Choose file and upload image
An image can be found in static/images/image.jpeg for convenience. 
Click "Choose File" and select image.jpeg
Click "Upload Image"
==========================================================================================================================================================================================
8. Choose the mode
Remarks: If predicted image does not show immediately, kindly wait since the backend processing in FastSAM is resolving some conflict (Would automatically be resolved - Tintker). 

**Everything**
Click "Confirm and Predict Mask" to send an api call to the api service in the docker container.

**Box**
Provide 4 integers x1,y1,x2,y2 (e.g 200,400,300,500).
Click "Draw Box and Preview" to verify bounding box.
Click "Confirm and Predict Mask (Box)" to send an api call to the api service in the docker container.

**Text**
Provide a sentence/text (e.g. This is a white cat).
Click "Confirm and Predict Mask (Text)" to send an api call to the api service in the docker container.

**Points**
Provide 2 integers x1,y1 (e.g. 200,300) for first point box and 1 integer (e.g. 1 - Mask, 0 -No Mask) for the second label box.
To add more fields, click "Add Field" and provide the respective inputs.
Click "Draw Points and Preview" to verify points.
Click "Confirm and Predict Mask (Points)" to send an api call to the api service in the docker container.
==========================================================================================================================================================================================
Additional remarks:
There are some checks done in both the frontend and backend (e.g. assertions, pydantic, regex)
Pytest is used for unit testing for the api service.
Thank you for you time!
