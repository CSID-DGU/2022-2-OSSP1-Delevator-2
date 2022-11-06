"""Perform test request"""
import pprint

import requests
import time
import numpy as np
import cv2

k = False

def capture():
    cap = cv2.VideoCapture(0) # 노트북 웹캠을 카메라로 사용
    cap.set(3,640) # 너비
    cap.set(4,480) # 높이

    ret, frame = cap.read() # 사진 촬영
    frame = cv2.flip(frame, 1) # 좌우 대칭

    cv2.imwrite('webcam_pic.jpg', frame) # 사진 저장
        
    cap.release()
    cv2.destroyAllWindows()
    k = True
    return k


while True:
    capture()

    if k == True:
        DETECTION_URL = "http://localhost:5000/v1/object-detection/yolov5s"
        # TEST_IMAGE = "/workspace/yo/YOLOv5-Flask/data/images/webcam_pic.jpg"
        TEST_IMAGE = "webcam_pic.jpg"

        image_data = open(TEST_IMAGE, "rb").read()

        response = requests.post(DETECTION_URL, files={"image": image_data}).json()

        pprint.pprint(response)
        k = False

        time.sleep(5)
