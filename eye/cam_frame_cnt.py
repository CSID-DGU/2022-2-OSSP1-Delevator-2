import cv2
import time

cap = cv2.VideoCapture(0)

start = time.time()
count = 0

while True:
    ret, frame = cap.read()
    count += 1
    if time.time() - start >= 10:
        break

print("10초 동안 들어온 frame 개수 : ", count)

cap.release()
cv2.destroyAllWindows()

