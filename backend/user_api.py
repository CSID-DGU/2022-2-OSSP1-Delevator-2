"""
백엔드 22.11.06.
1. Flask 서버에서 OpenCV로 웹캠 영상 받아오기 -> 모델에 저장할 수 있는 파일 생성
2. 프로토콜 처리
"""
import os
import sys
from flask import Flask, render_template, Response, url_for, redirect, session, request
import cv2
import time
import datetime
import schedule
import random
import torch
path='C:/Users/User/PycharmProjects/opensw_proj'
os.chdir(path)

app = Flask(__name__)
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)
app.secret_key = 'delevator'
condition = [1,1,1,1]
array = [0,0,0,0]
global cheating_class

# yolo model 불러오기
#model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)  # force_reload to recache

# POST 통신으로 들어오는 이미지를 저장하고 모델로 추론하는 과정
def save_image(file):
    file.save("YOLOv5-Flask/api_pic/req.jpg")

@app.route('/')
def web():
    return "team delevator start"

# check objects
# person, backpack, handbag, suitcase, dining table, cell phone, book


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        save_image(file)  # 들어오는 이미지 저장
        # train_img = './temp/' + file.filename
        train_img = '"YOLOv5-Flask/api_pic/req.jpg"'
        temp = model(train_img)
        result = temp.pandas().xyxy[0]['name']
        check = True  # check
        # answer = ""
        # for i in range(len(result)):
        #     if result[i] == "no-mask":
        #         check = False
        #         answer = "Detect"
        #         break

        # if check:
        #     answer = "Safe"

        # name = file.filename

        # res = {
        #     'answer' : answer,
        #     'name'   : name
        # }
        # os.remove('./temp/'+file.filename)

        # return res
        print(result)
        return result


@app.route('/')
def index(exam_name = 'ossp_중간고사'):
    """Video streaming home page."""
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    condition_msg = check_condition(condition)
    templateData = {
            'title':'Image Streaming',
            'time': timeString,
            'exam': exam_name,
            'conditions': condition_msg
            }
    return render_template('index.html', **templateData)

def check_condition(condition):
    """
    부정행위 조건 체크해서 부정행위 종류별 메세지 출력해주는 함수
    :param condition: 부정행위 조건 여부 리스트
                    (0: 응시자의 얼굴이 잘 보이는지,
                    1: 책상에 책 및 교안 유무,
                    2: 핸드폰 존재 유무,
                    3: 소리를 통한 제 3자 개입 유무)
    :return: 문자열 리스트
    """
    condition_msg = ''
    condition_names = {0 : '얼굴 전체가 나오도록 각도를 조정해주세요.\n',
                       1: '책상이 나오도록 각도를 조정해주세요.\n',
                       2: '책상이 나오도록 각도를 조정해주세요.\n',
                       3: '마이크를 켜주세요.\n'}
    for i, c in enumerate(condition):
        if (i!=2 and c == 1) or (i==2 and c==1 and condition[1] != 1):
            condition_msg += condition_names[i]
    return condition_msg

def gen_frames(sid='000000', condition = [1,1,1,1]):
    """
    웹캠 프레임 생성
    :param sid: 학생 번호(default : '000000')
    :param condition: 부정행위 조건 여부 리스트
    :return:
    """
    camera = cv2.VideoCapture(0) #윈도우에 설치된 Defrault 카메라로 영상 촬영
    _, frame = camera.read()
    width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fps = 30
    out = cv2.VideoWriter(sid+'_video.avi', fourcc, fps, (int(width), int(height))) # 학번_video.avi로 저장
    schedule.every(1).seconds.do(predict) #약 0.1초에 1개씩 출력하도록 스케줄링 (보통 1초에 9~12개)
    time.sleep(0.2)
    lastTime = time.time() * 1000.0
    frame_cnt = 0

    while True:
        ret, image = camera.read()

        results = model(frame, size=320)  # reduce size=320 for faster inference
        print(results)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6)
        delt = time.time() * 1000.0 - lastTime
        s = str(int(delt))
        # print (delt," Found {0} faces!".format(len(faces)) )
        lastTime = time.time() * 1000.0
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            #cv2.circle(image, (int(x + w / 2), int(y + h / 2)), int((w + h) / 3), (255, 255, 255), 3)
            cv2.rectangle(image, (x,y,w,h), (255, 255, 255), 3)
            cv2.putText(image, "face", (x-5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #cv2.putText(image, "face", faces, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0),2)
        #cv2.putText(image, condition_msg, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        now = datetime.datetime.now()
        timeString = now.strftime("%Y-%m-%d %H:%M")
        cv2.putText(image, timeString, (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        #cv2.putText(image, sid, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # cv2.imshow("Frame", image)
        out.write(image)

        schedule.run_pending()  # 위에서 스케줄링 한 시간마다 수행
        frame_cnt += 1

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        de_buf = cv2.imdecode(buffer)


        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()
    out.realease()
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
