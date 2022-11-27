# pip install -r requirements.txt
# python eye_test.py 하면 실행됨

import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking() # object 만들기
webcam = cv2.VideoCapture(0) # webcam 열기

while True:
    # 웹캠으로 영상 받기
    _, frame = webcam.read()

    # import gazetracking 에서 분석
    gaze.refresh(frame)

    frame = gaze.annotated_frame() # 분석된 영상
    text = ""

    if gaze.is_blinking(): # 눈 감았을 때
        text = "Blinking"
    elif gaze.is_right(): # 오른쪽을 보고 있을 때
        text = "Looking right"
    elif gaze.is_left(): # 왼쪽을 보고 있을 때
        text = "Looking left"
    elif gaze.is_center(): # 정면을 보고 있을 때
        text = "Looking center"

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2) # 글자 쓰기

    left_pupil = gaze.pupil_left_coords() # 왼쪽 눈 좌표
    right_pupil = gaze.pupil_right_coords() # 오른쪽 눈 좌표
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1) # 글자 쓰기
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1) # 글자 쓰기

    cv2.imshow("Demo", frame) # 영상 보여주기

    if cv2.waitKey(1) == 27:
        break
   
webcam.release()
cv2.destroyAllWindows()