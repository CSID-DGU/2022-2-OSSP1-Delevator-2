#!/usr/bin/env python
from flask import Flask, render_template, Response
import io
import cv2
import torch
from PIL import Image

app = Flask(__name__)
vc = cv2.VideoCapture(0)
model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)  # force_reload to recache

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
        # results = model(frame, size=320)  # reduce size=320 for faster inference
        # print(results)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
