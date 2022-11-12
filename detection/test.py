import io
from pickletools import read_uint1
from torchvision import models
import json
from flask import Flask, jsonify, request, render_template, Response
from flask import make_response
import torchvision.transforms as transforms
import torch
from PIL import Image
import os
import cv2
import time

app = Flask(__name__)

model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)

cap = cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    while True:
        t0 = time.time()
        success, frame = cap.read()  # read the camera frame
        results = model(frame)
        print()
        
        results.render() # 결과 렌더링
        obj = results.pandas().xyxy[0].to_json(orient="records") # 물체의 이름과 bounding box의 좌표
        print(obj)
        
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', results.ims[-1]) # 더 효율적인 방법이 있을까?
            frame = buffer.tobytes()
            
            t1 = time.time()
            
            print("time : {:.4f}s".format(t1 - t0))
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
