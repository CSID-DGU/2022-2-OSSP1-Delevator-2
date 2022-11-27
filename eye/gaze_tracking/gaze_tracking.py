from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration


class GazeTracking(object): # 시선인식 클래스

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration() # Calibration 클래스 객체 생성

        self._face_detector = dlib.get_frontal_face_detector() # 얼굴 인식

        cwd = os.path.abspath(os.path.dirname(__file__)) # 현재 파일의 절대 경로
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat")) # 모델 파일 경로
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def pupils_located(self): # 눈동자 위치가 정확히 인식되었는지 확인

        try:
            int(self.eye_left.pupil.x) # 눈동자의 x 좌표가 정수형이면 True
            int(self.eye_left.pupil.y) # 눈동자의 y 좌표가 정수형이면 True
            int(self.eye_right.pupil.x) # 눈동자의 x 좌표가 정수형이면 True
            int(self.eye_right.pupil.y) # 눈동자의 y 좌표가 정수형이면 True
            return True # 모두 True이면 True 반환
        except Exception:
            return False

    def _analyze(self): # 눈동자 위치 인식

        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY) # 흑백으로 변환
        faces = self._face_detector(frame) # 얼굴 인식

        try:
            landmarks = self._predictor(frame, faces[0]) # 랜드마크 인식
            self.eye_left = Eye(frame, landmarks, 0, self.calibration) # 왼쪽 눈 인식
            self.eye_right = Eye(frame, landmarks, 1, self.calibration) # 오른쪽 눈 인식

        except IndexError: # 얼굴 인식 실패
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame): # 프레임을 받아서 분석

        self.frame = frame # 프레임 저장
        self._analyze() # 눈동자 위치 인식

    def pupil_left_coords(self): # 왼쪽 눈동자 좌표
    
        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            x = self.eye_left.origin[0] + self.eye_left.pupil.x # 왼쪽 눈의 원점 x 좌표 + 눈동자의 x 좌표
            y = self.eye_left.origin[1] + self.eye_left.pupil.y # 왼쪽 눈의 원점 y 좌표 + 눈동자의 y 좌표
            return (x, y) # 눈동자의 좌표 반환

    def pupil_right_coords(self): # 오른쪽 눈동자 좌표

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            x = self.eye_right.origin[0] + self.eye_right.pupil.x # 오른쪽 눈의 원점 x 좌표 + 눈동자의 x 좌표
            y = self.eye_right.origin[1] + self.eye_right.pupil.y # 오른쪽 눈의 원점 y 좌표 + 눈동자의 y 좌표
            return (x, y) # 눈동자의 좌표 반환
 
    def horizontal_ratio(self): # 눈동자의 x 좌표 비율

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10) # 왼쪽 눈동자의 x 좌표 / (왼쪽 눈의 중심 x 좌표 * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10) # 오른쪽 눈동자의 x 좌표 / (오른쪽 눈의 중심 x 좌표 * 2 - 10)
            return (pupil_left + pupil_right) / 2 # 두 눈동자의 x 좌표 비율의 평균 반환

    def vertical_ratio(self): # 눈동자의 y 좌표 비율

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10) # 왼쪽 눈동자의 y 좌표 / (왼쪽 눈의 중심 y 좌표 * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10) # 오른쪽 눈동자의 y 좌표 / (오른쪽 눈의 중심 y 좌표 * 2 - 10)
            return (pupil_left + pupil_right) / 2 # 두 눈동자의 y 좌표 비율의 평균 반환

    def is_right(self): # 오른쪽을 보고 있는지 확인

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            return self.horizontal_ratio() <= 0.4 # 눈동자의 x 좌표 비율이 0.4 이하이면 오른쪽을 보고 있음

    def is_left(self): # 왼쪽을 보고 있는지 확인

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            return self.horizontal_ratio() >= 0.65 # 눈동자의 x 좌표 비율이 0.65 이상이면 왼쪽을 보고 있음

    def is_center(self): # 정면을 보고 있는지 확인

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            return self.is_right() is not True and self.is_left() is not True # 오른쪽을 보고 있지 않고, 왼쪽을 보고 있지 않으면 정면을 보고 있음

    def is_blinking(self): # 눈을 감고 있는지 확인

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2 # 두 눈의 눈 감음 비율의 평균
            return blinking_ratio > 4 # 눈 감음 비율이 4 이상이면 눈을 감고 있음

    def annotated_frame(self): # 눈동자 위치를 표시한 프레임 반환

        frame = self.frame.copy() # 프레임 복사

        if self.pupils_located: # 눈동자 위치가 정확히 인식되었으면
            color = (0, 255, 0) # 눈동자 위치가 정확히 인식되었으면 초록색
            x_left, y_left = self.pupil_left_coords() # 왼쪽 눈동자의 좌표
            x_right, y_right = self.pupil_right_coords() # 오른쪽 눈동자의 좌표
            cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color) # 왼쪽 눈동자의 x 좌표에 세로선 그리기
            cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color) # 왼쪽 눈동자의 y 좌표에 가로선 그리기
            cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color) # 오른쪽 눈동자의 x 좌표에 세로선 그리기
            cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color) # 오른쪽 눈동자의 y 좌표에 가로선 그리기

        return frame # 눈동자 위치를 표시한 프레임 반환