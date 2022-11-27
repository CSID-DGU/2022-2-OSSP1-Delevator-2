import math
import numpy as np
import cv2
from .pupil import Pupil


class Eye(object): # 눈을 찾는 class

    LEFT_EYE_POINTS = [36, 37, 38, 39, 40, 41] # 왼쪽 눈의 landmark point
    RIGHT_EYE_POINTS = [42, 43, 44, 45, 46, 47] # 오른쪽 눈의 landmark point

    def __init__(self, original_frame, landmarks, side, calibration): 
        self.frame = None
        self.origin = None
        self.center = None
        self.pupil = None
        self.landmark_points = None

        self._analyze(original_frame, landmarks, side, calibration) 

    @staticmethod
    def _middle_point(p1, p2): # 눈의 중간 지점을 찾는 함수

        x = int((p1.x + p2.x) / 2) # x좌표의 중간 지점
        y = int((p1.y + p2.y) / 2) # y좌표의 중간 지점
        return (x, y) # 중간 지점의 좌표를 반환

    def _isolate(self, frame, landmarks, points): # 눈을 isolate 하는 함수

        region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in points]) # 눈의 landmark point를 numpy array로 변환
        region = region.astype(np.int32) # numpy array를 int32로 변환
        self.landmark_points = region # 눈의 landmark point를 저장

        height, width = frame.shape[:2] # frame의 height와 width를 저장
        black_frame = np.zeros((height, width), np.uint8) # black frame을 생성
        mask = np.full((height, width), 255, np.uint8) # mask를 생성
        cv2.fillPoly(mask, [region], (0, 0, 0)) # mask에 눈의 landmark point를 fill
        eye = cv2.bitwise_not(black_frame, frame.copy(), mask=mask) # mask를 이용하여 눈을 isolate

        margin = 5 # 눈의 margin
        min_x = np.min(region[:, 0]) - margin # 눈의 x좌표의 최소값
        max_x = np.max(region[:, 0]) + margin # 눈의 x좌표의 최대값
        min_y = np.min(region[:, 1]) - margin # 눈의 y좌표의 최소값
        max_y = np.max(region[:, 1]) + margin # 눈의 y좌표의 최대값

        self.frame = eye[min_y:max_y, min_x:max_x] # 눈의 frame을 저장
        self.origin = (min_x, min_y) # 눈의 좌측 상단 좌표를 저장

        height, width = self.frame.shape[:2] # 눈의 frame의 height와 width를 저장
        self.center = (width / 2, height / 2) # 눈의 중심 좌표를 저장

    def _blinking_ratio(self, landmarks, points): # 눈을 감았는지 확인하는 함수

        left = (landmarks.part(points[0]).x, landmarks.part(points[0]).y) # 눈의 왼쪽 지점
        right = (landmarks.part(points[3]).x, landmarks.part(points[3]).y) # 눈의 오른쪽 지점
        top = self._middle_point(landmarks.part(points[1]), landmarks.part(points[2])) # 눈의 위쪽 지점
        bottom = self._middle_point(landmarks.part(points[5]), landmarks.part(points[4])) # 눈의 아래쪽 지점

        eye_width = math.hypot((left[0] - right[0]), (left[1] - right[1])) # 눈의 width
        eye_height = math.hypot((top[0] - bottom[0]), (top[1] - bottom[1])) # 눈의 height

        try:
            ratio = eye_width / eye_height # 눈의 width와 height의 비율
        except ZeroDivisionError:
            ratio = None

        return ratio # 눈의 width와 height의 비율을 반환

    def _analyze(self, original_frame, landmarks, side, calibration): # 눈을 분석하는 함수

        if side == 0: # 왼쪽 눈일 경우
            points = self.LEFT_EYE_POINTS # 왼쪽 눈의 landmark point를 저장
        elif side == 1: # 오른쪽 눈일 경우
            points = self.RIGHT_EYE_POINTS # 오른쪽 눈의 landmark point를 저장
        else:
            return

        self.blinking = self._blinking_ratio(landmarks, points) # 눈을 감았는지 확인
        self._isolate(original_frame, landmarks, points) # 눈을 isolate
 
        if not calibration.is_complete():   # calibration이 완료되지 않았을 경우
            calibration.evaluate(self.frame, side) # calibration을 진행

        threshold = calibration.threshold(side) # calibration의 threshold를 저장
        self.pupil = Pupil(self.frame, threshold) # 눈동자를 검출
