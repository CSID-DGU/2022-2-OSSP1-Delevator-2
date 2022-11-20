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
    t0 = time.time() # 처음 시작할 때 시간 초기화
    while True:
        success, frame = cap.read()  # read the camera frame
        
        if time.time() - t0 > 0.8: # 1초 간격으로 프레임 받아서 전달 (모델 처리가 0.2초 정도 걸리기 때문에 0.8초로 설정)
            results = model(frame)
            print()
            results.render() # bounding box가 나타난 결과를 이미지로 렌더링
            obj = results.pandas().xyxy[0].to_json(orient="records") # 물체의 이름과 bounding box의 좌표

            if len(obj) > 2:
                print(obj)
            
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', results.ims[-1]) # 더 효율적인 방법이 있을까?
                frame = buffer.tobytes() # 바이트로 변환
                
                t1 = time.time()
                
                print("time : {:.4f}s".format(t1 - t0)) # 시간 측정
                
                t0 = time.time() # 새로운 기준 시간 측정
                
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        else:
            # 1초 안넘었을 경우 모델에 넣지 않고 프레임만 보냄
            if success:
                _, buffer = cv2.imencode('.jpg', frame) # 더 효율적인 방법이 있을까?
                frame = buffer.tobytes() # 바이트로 변환
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
