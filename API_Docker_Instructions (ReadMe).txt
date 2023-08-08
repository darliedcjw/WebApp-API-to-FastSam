**There are a total of 7 steps**
==========================================================================================================================================================================================
1. cd to "api" folder
==========================================================================================================================================================================================
2. Build Docker Image from Dockerfile
docker build -t api-service-docker .
==========================================================================================================================================================================================
3.  Run Container in background
[Command]: docker run -d <docker image>
e.g. docker run -d -it api-service-docker
==========================================================================================================================================================================================
4.  Check Container ID
[Command]: docker ps
**Take note of the <first 4 characters> of the Container ID
 ==========================================================================================================================================================================================
5.  Create another bash terminal within Docker Container
[Command]: docker exec -it <first 4 characters> bash
==========================================================================================================================================================================================
6.  API Commands:
*OPTIONAL* help command: python api_call.py -h

===Ping===
 [Command]: python api_call.py -s 'ping'

==Infer===
[optional arg]
-ip: Path to image, Default: 'FastSAM/images/cat.jpg'
-bp: Parameters for box, Default: "{'box_prompt': [[.0,.0,.5,.5]]}"
-tp: Parameters for text, Default: "{'text_prompt': 'This is a white cat'}"
-pp: Parameters for points, Default: "{'point_prompt': [[.3,.5],[.7,.3],[.4,.4]], 'point_label': [0,0,1]}"

1. Everything
[Command]: python api_call.py -s 'infer' -m 'everything'

2. Box
[Command]: python api_call.py -s 'infer' -m 'box'

3. Text
[Command]: python api_call.py -s 'infer' -m 'text'

4. Points
[Command]: python api_call.py -s 'infer' -m 'points'
==========================================================================================================================================================================================
7. Exit Bash
[Command]: exit
==========================================================================================================================================================================================
8.  Copy output images from container to local
[Command]: docker cp <first 4 characters>:/api/output <destination>
e.g. docker cp f8ff:/api/output .
**Take note of your working directory for the destination
**[For windows]: Alternative, you can use Docker Desktop to retrieve the image.
==========================================================================================================================================================================================
THANK YOU FOR YOUR TIME!