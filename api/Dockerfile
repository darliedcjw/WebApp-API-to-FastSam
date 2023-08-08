FROM python:3.11
COPY . /api
WORKDIR /api
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python
EXPOSE 4000
ENTRYPOINT [ "python" ]
CMD [ "api.py" ]