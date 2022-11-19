#!/usr/bin/env python
import os
from flask import Flask, render_template, Response, flash, request
from pathlib import Path
import io
import cv2
import torch
from PIL import Image
import time
from datetime import datetime

app = Flask(__name__)
vc = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
model = torch.hub.load("ultralytics/yolov5", "yolov5s",
                       force_reload=True)  # force_reload to recache
#model.load_state_dict(torch.load('yolov5s.pt'), strict=False)
# model.eval()


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html', cheating_history=cheating_history)

# 감지된 부정행위 리스트 저장
# Dictionary의 List 형태. Dictionary의 key는 'time', 'cheating_list', 'imgName'로 구성
cheating_history = []

# @app.route('/get_webcam')
# @app.route ('/detect_cheating', methods=['POST'])
def gen():
    """Video streaming generator function."""
    # if request.method == 'POST':
    t0 = time.time()
    i = 0
    while True:
        success, frame = vc.read()

        if time.time() - t0 > 0.8:
            #encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
            #io_buf = io.BytesIO(image_buffer)

            if not success:
                break
            else:
                # reduce size=320 for faster inference
                results = model(frame, size=320)
                # print(results)
                #objs = results.pandas().xyxy[0]['name']
                json_result = results.pandas(
                ).xyxy[0].to_json(orient='records')
                result = results.pandas().xyxy[0]

                print(result['name'])
                # print(result)
                # objs.render()  # 결과 렌더링

                # 부정행위 감지
                cheating_list = detect_cheating(result['name'])
                print(cheating_list)
                # 부정행위 경고 메세지 출력
                warning_msg = gen_warning_msg(cheating_list)
                print(warning_msg)

                ret, buffer = cv2.imencode(
                    '.jpg', results.ims[-1])  # 더 효율적인 방법이 있을까?
                frame = buffer.tobytes()  # 바이트로 변환

                t1 = time.time()

                print("time : {:.4f}s".format(t1 - t0))  # 시간 측정

                t0 = time.time()  # 새로운 기준 시간 측정

                if len(cheating_list) > 0:
                    # 부정행위가 감지되면
                    now = datetime.now()
                    # 부정행위 순간 캡처 이미지 파일 저장
                    folderPath = Path('backend/captureHistory/').absolute().as_uri()[7:]+'/'
                    nowtime = now.strftime("%Y%m%d_%H%M%S")
                    imgPath = os.path.join(folderPath, nowtime + '.jpg')
                    print(imgPath)
                    cv2.imwrite(imgPath, results.ims[-1])
                    
                    # 부정행위 리스트에 추가 (Dictionary 형태로 저장)
                    cheating_history.append({'time': nowtime, 'cheating_list': cheating_list, 'imgName': (nowtime + '.jpg')})
                    print(cheating_history)
                    
                # concat frame one by one and show result
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # 1초 안넘었을 경우 모델에 넣지 않고 프레임만 보냄
            if success:
                _, buffer = cv2.imencode('.jpg', frame)  # 더 효율적인 방법이 있을까?
                frame = buffer.tobytes()  # 바이트로 변환
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        i += 1

    vc.release()
    cv2.destroyAllWindows()


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


def detect_cheating(result):
    """
    객체감지 모델에서 감지한 객체 중 부정행위에 포함되는 객체를 반환해주는 함수
    Args:
        result: 객체감지 모델 predict 결과

    Returns: 부정행위에 포함되는 객체 list

    """
    cheating_obj_list = ['cell phone', 'book']
    cheating_list = []
    person_cnt = 0
    for i, obj in enumerate(result):
        if obj == 'person':
            # 사람 수 2명 이상이면 부정행위로 인식
            person_cnt += 1
        if (obj in cheating_obj_list) or (obj == 'person' and person_cnt > 1):
            cheating_list.append(obj)

    return cheating_list


def gen_warning_msg(cheating_list):
    """
    부정행위 객체가 감지되면 부정행위 객체별로 경고 메세지 생성하는 함수
    Args:
        cheating_list: 부정행위에 포함되는 객체 list

    Returns: 경고 메세지

    """
    person_cnt = 0  # 사람 수
    warning_msg = ''  # 경고 메세지 리스트
    for obj in cheating_list:
        if obj == 'person':
            # 사람 수 2명 이상이면 부정행위로 인식
            person_cnt += 1
        if person_cnt >= 2:
            warning_msg += '두명 이상이 감지되었습니다. '
        elif obj == 'cell phone':
            # 핸드폰이 감지됐을 경우
            warning_msg += '핸드폰이 감지되었습니다. '
        elif obj == 'book':
            # 교안이 감지됐을 경우
            warning_msg += '교안이 감지되었습니다. '

    # print(warning_msg)
    return warning_msg


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True, port=8080)
