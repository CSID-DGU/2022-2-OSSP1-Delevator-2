"""Perform test request"""
import pprint

import requests
import time
import numpy as np
import cv2

k = False


def capture():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 노트북 웹캠을 카메라로 사용
    # cap.set(3,640) # 너비
    # cap.set(4,480) # 높이

    ret, frame = cap.read()  # 사진 촬영
    frame = cv2.flip(frame, 1)  # 좌우 대칭

    cv2.imwrite('webcam_pic.jpg', frame)  # 사진 저장

    cap.release()


'''
- 시간 측정 코드 추가
- 변수 k 삭제 
- ctrl + c로 종료 시 평균 시간 계산
- 딕셔너리 안의 부정행위로 의심되는 물품이 있는지 확인
'''
if __name__ == "__main__":
    DETECTION_URL = "http://localhost:5000/v1/object-detection/yolov5s"
    sum = 0
    count = 0

    try:
        while True:
            t0 = time.time()

            tic = time.time()
            capture()
            toc = time.time()
            print("Capturing image.... : {:.2f}s".format(toc - tic))

            # TEST_IMAGE = "/workspace/yo/YOLOv5-Flask/data/images/webcam_pic.jpg"
            TEST_IMAGE = "webcam_pic.jpg"

            tic = time.time()
            image_data = open(TEST_IMAGE, "rb").read()
            toc = time.time()
            # print("Loading image.... : {:.2f}s".format(toc - tic))

            tic = time.time()
            response = requests.post(DETECTION_URL, files={
                                     "image": image_data}).json()
            toc = time.time()
            print("Requesting results.... : {:.2f}s".format(toc - tic))

            # tic = time.time()
            # pprint.pprint(response)
            # toc = time.time()
            # print("Showing results.... : {:.2f}s".format(toc - tic))

            # 딕셔너리 안의 부정행위로 의심되는 물품이 있는지 확인
            for r in response:
                if (r['name'] == 'cell phone' and r['confidence'] > 0.55) or\
                   (r['name'] == 'book' and r['confidence'] > 0.55):
                    print("Warning : {} detected".format(r['name']))

            t1 = time.time()

            print("Total : {:.4f}s".format(t1 - t0))
            sum += t1 - t0
            count += 1

            # k = False

            # time.sleep(5)

    except KeyboardInterrupt:
        print("avg : {:.4f}s".format(sum / count))
