from flask import Flask
import cv2

app = Flask(__name__)


@app.route('/')
def hello():
    webcam = cv2.VideoCapture(0)

    if not webcam.isOpened():
        print("Webcam not found")
        exit()

    while webcam.isOpened():
        status, frame = webcam.read()
        if status:
            cv2.imshow("test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    webcam.release()
    cv2.destroyAllWindows()
    return "Hello, World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
