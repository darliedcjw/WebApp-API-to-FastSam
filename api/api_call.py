import requests
import argparse
import json

def api_call(
        service,
        image_path,
        mode,
        box_params,
        text_params,
        points_params
):
    

    url = 'http://localhost:4000/' + service
    print(url)

    # Ping Service
    if service == 'ping':
        response = requests.post(url)

        # Check the response status code to verify if the request was successful
        if response.status_code == 200:
            print(json.dumps({
                'message': 'pong'
                }))
        else:
            print('Server is down!')           

    # Infer Service
    elif service == 'infer':
        # Path to Image [Upload]
        image_path = 'FastSAM/images/cat.jpg'

        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}

            # # everything
            if mode == 'everything':
                data = {
                    'mode': 'everything'
                }
            
            ## box
            elif mode == 'box':
                data = {
                    'mode': 'box',
                    'data': box_params
                }

                print(data)

            # text
            elif mode == 'text':
                data = {
                    'mode': 'text',
                    "data": text_params
                }

            # points
            elif mode == 'points':
                data = {
                    'mode': 'points',
                    'data': points_params
                }
                
            response = requests.post(url, files=files, data=data)

        # Check the response status code to verify if the request was successful
        if response.status_code == 200:
            result = 'Inference completed!'
            print(result)
        else:
            print('Failed to perform inference.')                


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', '-s', help='API service.', type=str, default='ping')
    parser.add_argument('--image_path', '-ip', help='Path to image file.', type=str, default='FastSAM/images/cat.jpg')
    parser.add_argument('--mode', '-m', help='Selection of mode.', type=str, default='everything')
    parser.add_argument('--box_params', '-bp', help='Parameters for box. For example: "{\'box_prompt\': [[x_top_left,y_top_left,x_bottom_right,y_bottom_right]]}"', type=str, default="{'box_prompt': [[.0,.0,.5,.5]]}")
    parser.add_argument('--text_params', '-tp', help='Parameters for text. For example: "{\'text_prompt\': \'Whatever I want to type!\'}"', type=str, default="{'text_prompt': 'This is a white cat'}")
    parser.add_argument('--points_params', '-pp', help='Parameters for points. For example: "{\'point_prompt\': [[x1,y1],[x2,y2]], \'point_label\': [0,1]}"', type=str, default="{'point_prompt': [[.3,.5],[.7,.3],[.4,.4]], 'point_label': [0,0,1]}")
    args = parser.parse_args()
    
    api_call(**args.__dict__)
