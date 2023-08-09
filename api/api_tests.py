import requests
ENDPOINT_URL = 'http://localhost:4000'


# tests the ping route from the app
def test_ping_route():

    # act
    response = requests.get(ENDPOINT_URL + '/ping')
    
    # assert
    assert response.status_code == 200
    assert response.json() == {"message":"pong"}

# testing the successful completion of the mode == everything with all expected parameters provided (i.e. nothing)
def test_infer_route_mode_everything_success():
    
    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'everything'
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)
    
    # assert
    assert response.status_code == 200


# testing the successful completion of the mode == text with all expected parameters provided
def test_infer_route_mode_text_success():
    
    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'text',
        'data': "{'text_prompt': 'This is a white cat'}"
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)

    # assert
    assert response.status_code == 200

# testing that the the mode = text functionality does not pass validation when no text is provided
def test_infer_route_mode_text_failure_no_text_provided():

    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'text',
        'data': "{'text_prompt': ''}"
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)

    # assert
    assert response.status_code == 500

# testing the successful completion of the mode == points with all expected parameters provided
def test_infer_route_mode_points_success():

    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'points',
        'data': "{'point_prompt': [[.1,.2],[.3,.4]], 'point_label': [0,1]}"
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)

    # assert
    assert response.status_code == 200

# testing that the the mode = points functionality does not pass validation when differing numbers of items are present in point_prompt and point_label
def test_infer_route_mode_points_failure_point_prompt_2_items_point_label_3_items():

    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'points',
        'data': "{'point_prompt': [[.1,.2],[.3,.4]], 'point_label': [0,1,0]}"
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)

    # assert
    assert response.status_code == 500

# testing the successful completion of the mode == box with all expected parameters provided
def test_infer_route_mode_box_success():
    
    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'box',
        'data': "{'box_prompt': [[.1,.2,.3,.4]]}"
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)

    # assert
    assert response.status_code == 200


# testing that the the mode = box functionality does not pass validation when too few coordinates are provided
def test_infer_route_mode_box_failure_not_enough_coordinates():
    
    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'box',
        'data': "{'box_prompt': [[.1,.2,.3]]}" # only 3 points provided, test should fail
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)

    # assert
    assert response.status_code == 500

# testing that the the mode = box functionality does not pass validation when too many coordinates are provided
def test_infer_route_mode_box_failure_too_many_coordinates():
    
    # arrange
    files = {
        'image': ('image.jpeg', open('tests/image.jpeg', 'rb'))
    }

    data = {
        'mode': 'box',
        'data': "{'box_prompt': [[.1,.2,.3,.4,.5]]}" # only 3 points provided, test should fail
    }

    # act
    response = requests.post(ENDPOINT_URL + '/infer', files=files, data=data)

    # assert
    assert response.status_code == 500