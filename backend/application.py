#!/usr/bin/env python
from flask import Flask, render_template, Response, flash
import io
import cv2
import torch
from PIL import Image

app = Flask(__name__)
vc = cv2.VideoCapture(0)
model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)  # force_reload to recache
model.load_state_dict(torch.load('yolov5s.pt'), strict=False)
model.eval()


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')



def gen():
    """Video streaming generator function."""
    while True:
        read_return_code, frame = vc.read()
        encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(image_buffer)
        
        # 모델에 사진 넣기 -> 이 코드만 넣으면 송출이 안됨
        results = model(frame, size=320)  # reduce size=320 for faster inference
        #print(results)
        result = results.pandas().xyxy[0]['name']
        #print(type(result))
        print(result)

        # 부정행위 감지
        cheating_list = detect_cheating(result)
        print(cheating_list)
        # 부정행위 경고 메세지 출력
        warning_msg = gen_warning_msg(cheating_list)
        '''
        if warning_msg != "":
            flash(warning_msg)
            return render_template('index.html')
        '''
        print(warning_msg)
        #render_template('index.html', warning_txt = warning_msg)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')
        #return render_template('index.html')

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
    cheating_obj_list = ['cell phone', 'person']
    cheating_list = []
    for i, obj in enumerate(result):
        if obj in cheating_obj_list:
            cheating_list.append(obj)

    return cheating_list

def gen_warning_msg(cheating_list):
    """
    부정행위 객체가 감지되면 부정행위 객체별로 경고 메세지 생성하는 함수
    Args:
        cheating_list: 부정행위에 포함되는 객체 list

    Returns: 경고 메세지

    """
    person_cnt = 0 # 사람 수
    warning_msg = '' # 경고 메세지 리스트
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

    print(warning_msg)
    return warning_msg



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
