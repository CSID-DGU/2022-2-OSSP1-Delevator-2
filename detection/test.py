import json
from flask import Flask, jsonify, request, render_template, Response
from flask import make_response

import torch
import torchvision.transforms as transforms
from torchvision import models

import os
import cv2
import time
from PIL import Image
from gaze_tracking import GazeTracking

app = Flask(__name__)

model = torch.hub.load("ultralytics/yolov5", "custom", "teamD2.pt", force_reload=True)

cap = cv2.VideoCapture(0)



# @app.route('/test', methods=['GET'])
# def send_result(res):
#     # print("[result]")
#     # print(res)
#     # print(type(res))
#     for r in res:
#         print("confidence : {}".format(r['confidence']))
#     return 
        


def gen_frames():  # generate frame by frame from camera
    t0 = time.time() # 처음 시작할 때 시간 초기화
    gaze = GazeTracking() # object 만들기
    
    while True:
        success, frame = cap.read()  # read the camera frame
        gaze.refresh(frame)

        frame = gaze.annotated_frame() # 분석된 영상
        text = ""

        if gaze.is_blinking(): # 눈 감았을 때
            text = "Blinking"
        elif gaze.is_right(): # 오른쪽을 보고 있을 때
            text = "Looking right"
        elif gaze.is_left(): # 왼쪽을 보고 있을 때
            text = "Looking left"
        elif gaze.is_center(): # 정면을 보고 있을 때
            text = "Looking center"

        print(text)

        cv2.putText(frame, text, (60, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (147, 58, 31), 2) # 글자 쓰기
        left_pupil = gaze.pupil_left_coords() # 왼쪽 눈 좌표
        right_pupil = gaze.pupil_right_coords() # 오른쪽 눈 좌표
        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (60, 130), cv2.FONT_HERSHEY_DUPLEX, 1.5, (147, 58, 31), 2) # 글자 쓰기
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (60, 180), cv2.FONT_HERSHEY_DUPLEX, 1.5, (147, 58, 31), 2) # 글자 쓰기

        
        if time.time() - t0 > 0.0: # 1초 간격으로 프레임 받아서 전달 (모델 처리가 0.2초 정도 걸리기 때문에 0.8초로 설정)
            results = model(frame)
            print()
            results.render() # bounding box가 나타난 결과를 이미지로 렌더링
            obj = results.pandas().xyxy[0].to_json(orient="records") # 물체의 이름과 bounding box의 좌표
            if len(obj) > 2:
                print(obj)

            # send_result(results.pandas().xyxy[0])
            
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
    # app.run(debug=True, port=5000)
    # app.run(debug=True, port=8080)
    app.run()


