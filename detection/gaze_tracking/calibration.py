from __future__ import division
import cv2
from .pupil import Pupil


class Calibration(object): # Calibration 클래스

    def __init__(self):
        self.nb_frames = 20
        self.thresholds_left = []
        self.thresholds_right = []

    def is_complete(self): # 캘리브레이션 완료 여부 확인

        return len(self.thresholds_left) >= self.nb_frames and len(self.thresholds_right) >= self.nb_frames # 왼쪽, 오른쪽 눈 모두 캘리브레이션 완료

    def threshold(self, side): # 캘리브레이션 완료 후, 최종 threshold 계산
 
        if side == 0: # 왼쪽 눈
            return int(sum(self.thresholds_left) / len(self.thresholds_left)) # 왼쪽 눈의 threshold 평균
        elif side == 1: # 오른쪽 눈
            return int(sum(self.thresholds_right) / len(self.thresholds_right)) # 오른쪽 눈의 threshold 평균

    @staticmethod
    def iris_size(frame): # 눈의 크기 계산
 
        frame = frame[5:-5, 5:-5] # 눈의 테두리 제거
        height, width = frame.shape[:2] # 눈의 높이, 너비
        nb_pixels = height * width # 눈의 픽셀 수
        nb_blacks = nb_pixels - cv2.countNonZero(frame) # 눈의 흰색 픽셀 수
        return nb_blacks / nb_pixels # 눈의 흰색 픽셀 비율

    @staticmethod
    def find_best_threshold(eye_frame): # 최적의 threshold 계산

        average_iris_size = 0.48 # 평균 눈의 크기
        trials = {} # 시도 횟수

        for threshold in range(5, 100, 5): # 5 ~ 100 까지 5씩 증가
            iris_frame = Pupil.image_processing(eye_frame, threshold) # threshold 적용
            trials[threshold] = Calibration.iris_size(iris_frame) # 눈의 크기 계산
 
        best_threshold, iris_size = min(trials.items(), key=(lambda p: abs(p[1] - average_iris_size))) # 평균 눈의 크기와 가장 가까운 threshold 계산
        return best_threshold # 최적의 threshold 반환

    def evaluate(self, eye_frame, side): # 캘리브레이션 진행

        threshold = self.find_best_threshold(eye_frame) # 최적의 threshold 계산

        if side == 0: # 왼쪽 눈
            self.thresholds_left.append(threshold) # 왼쪽 눈의 threshold 저장
        elif side == 1: # 오른쪽 눈
            self.thresholds_right.append(threshold) # 오른쪽 눈의 threshold 저장
