#!/usr/bin/env python
import os
from flask import Flask, render_template, Response, flash, request, jsonify, send_from_directory
from pathlib import Path
import io
import cv2
import torch
from PIL import Image
import time
from datetime import datetime
import pandas as pd
from gaze_tracking import GazeTracking

app = Flask(__name__, static_folder='static')
vc = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='../teamD2.pt', force_reload=True)
#model.load_state_dict(torch.load('yolov5s.pt'), strict=False)
# model.eval()


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html', encoding='utf-8')

@app.route('/history/<filename>')
def loadImage(filename):
    return send_from_directory('static/captureHistory', filename);

# 감지된 부정행위 리스트 저장
# Dictionary의 List 형태. Dictionary의 key는 'time', 'cheating_list', 'imgName'로 구성
cheating_history = []

# @app.route('/get_webcam')
# @app.route ('/detect_cheating', methods=['POST'])
def gen():
    """Video streaming generator function."""
    # if request.method == 'POST':
    t0 = time.time()
    time_cnt = 0
    right_cnt = 0
    left_cnt = 0
    gaze = GazeTracking() # object 만들기
    warning_msg = ''
    
    while True:
        success, frame = vc.read()
        gaze.refresh(frame)

        frame = gaze.annotated_frame() # 분석된 영상
        text = ""

        if gaze.is_blinking(): # 눈 감았을 때
            text = "Blinking"
        elif gaze.is_right(): # 오른쪽을 보고 있을 때
            right_cnt += 1
            text = "Looking right"
        elif gaze.is_left(): # 왼쪽을 보고 있을 때
            text = "Looking left"
        elif gaze.is_center(): # 정면을 보고 있을 때
            left_cnt += 1
            text = "Looking center"

        print(text)
        print('left_cnt: ', str(left_cnt), 'right_cnt: ', str(right_cnt))

        # 10초마다 시선 부정행위 판별 & 초기화
        if time_cnt == 10:
            if left_cnt > 5:
                # 왼쪽 쳐다 보는 횟수가 10회 이상이면
                warning_msg = '시선이 왼쪽에 향해있습니다. 부정행위가 의심됩니다. '
            if right_cnt > 5:
                # 오른쪽 쳐다 보는 횟수가 10회 이상이면
                warning_msg += '시선이 오른쪽에 향해있습니다. 부정행위가 의심됩니다. '

            print(time.time(), ' ', warning_msg)
            #gaze_t0 = time.time() # gaze_t0 초기화
            left_cnt = 0 # 초기화
            right_cnt = 0 # 초기화
            time_cnt = 0 # 초기화

        if time.time() - t0 > 0.8:
            if not success:
                break
            else:
                # reduce size=320 for faster inference
                results = model(frame, size=320)
                json_result = results.pandas(
                ).xyxy[0].to_json(orient='records')
                result = results.pandas().xyxy[0]

                print(result[['name', 'confidence']])

                # 부정행위 감지
                cheating_df = detect_cheating(pd.DataFrame(result[['name', 'confidence']]))

                # 부정행위 경고 메세지 출력
                if warning_msg == '':
                    warning_msg = gen_warning_msg(cheating_df['object'])
                else:
                    warning_msg += gen_warning_msg(cheating_df['object'])
                print(warning_msg)

                ret, buffer = cv2.imencode(
                    '.jpg', results.ims[-1])  # 더 효율적인 방법이 있을까?
                frame = buffer.tobytes()  # 바이트로 변환

                t1 = time.time()

                print("time : {:.4f}s".format(t1 - t0))  # 시간 측정

                t0 = time.time()  # 새로운 기준 시간 측정

                if len(cheating_df) > 0:
                    # 부정행위가 감지되면
                    now = datetime.now()
                    # 부정행위 순간 캡처 이미지 파일 저장
                    folderPath = Path('backend/static/captureHistory').absolute().as_uri()[7:]+'/'
                    nowtime = now.strftime("%Y%m%d_%H%M%S")
                    imgPath = os.path.join(folderPath, nowtime + '.jpg')
                    print(imgPath)
                    cv2.imwrite(imgPath, results.ims[-1])
                    
                    # 부정행위 리스트에 추가 (Dictionary 형태로 저장)
                    cheating_history.append({'time': nowtime, 'cheating_list': list(cheating_df['object'].values),
                                             'warning_msg': warning_msg,
                                             'imgName': (nowtime + '.jpg')})
                    print(cheating_history)
                warning_msg = ''    # warning_msg 초기화
                    
                # concat frame one by one and show result
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # 1초 안넘었을 경우 모델에 넣지 않고 프레임만 보냄
            if success:
                _, buffer = cv2.imencode('.jpg', frame)  # 더 효율적인 방법이 있을까?
                frame = buffer.tobytes()  # 바이트로 변환
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time_cnt += 1   # 1초 반복 횟수 count

    vc.release()
    cv2.destroyAllWindows()


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
    
@app.route('/cheating_history', methods=['GET'])
def get_cheating_history():
    # cheating_history 리스트를 json 형태로 반환
    data = jsonify({"cheating_history":cheating_history})
    return data

def detect_cheating(result):
    """
    객체감지 모델에서 감지한 객체 중 부정행위에 포함되는 객체를 반환해주는 함수
    Args:
        result: 객체감지 모델 predict 결과(name, confidence)

    Returns: 부정행위에 포함되는 객체 list

    """
    cheating_obj_list = ['cell phone', 'book']
    cheating_list = []
    cheating_conf = []
    person_cnt = 0
    sum_conf = 0
    for i, res in enumerate(result.values):
        if res[0] in cheating_obj_list:
            if (res[0] == 'person') and (float(res[1]) > 0.6):
                # confidence 값이 0.6보다 클 때 사람 수 count
                person_cnt += 1
                sum_conf += float(res[1])

            if (res[0] != 'person') and (float(res[1]) > 0.6):
                # 핸드폰, 교안의 경우 confidence 값이 0.6보다 클 때 부정행위로 인식
                cheating_list.append(res[0])
                cheating_conf.append(float(res[1]))

            elif (res[0] == 'person') and (person_cnt > 1):
                # 사람일 경우 2명 이상일 때 부정행위로 인식
                cheating_list.append(res[0])
                cheating_conf.append(sum_conf / person_cnt)

    cheating_df = pd.DataFrame({'object': cheating_list, 'confidence': cheating_conf})
    print('**cheating_df**')
    print(cheating_df)

    return cheating_df


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
