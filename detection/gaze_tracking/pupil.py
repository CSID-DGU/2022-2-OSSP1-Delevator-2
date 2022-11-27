import numpy as np
import cv2


class Pupil(object): # 동공 체크 class

    def __init__(self, eye_frame, threshold):
        self.iris_frame = None
        self.threshold = threshold
        self.x = None
        self.y = None

        self.detect_iris(eye_frame) # 동공을 찾기 위한 이미지 처리

    @staticmethod
    def image_processing(eye_frame, threshold): # 동공을 찾기 위한 이미지 처리

        kernel = np.ones((3, 3), np.uint8) # 커널 생성
        new_frame = cv2.bilateralFilter(eye_frame, 10, 15, 15) # bilateralFilter를 이용한 노이즈 제거
        new_frame = cv2.erode(new_frame, kernel, iterations=3) # 침식 연산
        new_frame = cv2.threshold(new_frame, threshold, 255, cv2.THRESH_BINARY)[1] # 이진화

        return new_frame

    def detect_iris(self, eye_frame): # 동공을 찾는 함수

        self.iris_frame = self.image_processing(eye_frame, self.threshold) # 동공을 찾기 위한 이미지 처리

        contours, _ = cv2.findContours(self.iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        contours = sorted(contours, key=cv2.contourArea) # 동공의 크기를 기준으로 정렬

        try:
            moments = cv2.moments(contours[-2]) # 동공의 중심점을 찾기 위한 모멘트 계산
            self.x = int(moments['m10'] / moments['m00']) # 동공의 중심점 x좌표
            self.y = int(moments['m01'] / moments['m00']) # 동공의 중심점 y좌표
        except (IndexError, ZeroDivisionError): # 동공이 없는 경우
            pass
