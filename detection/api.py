import io
from pickletools import read_uint1
from torchvision import models
import json
from flask import Flask, jsonify, request
from flask import make_response
import torchvision.transforms as transforms
import torch
from PIL import Image
import os

app = Flask(__name__)

# yolo model 불러오기
model = torch.hub.load('./yolov5/', 'custom', path='YOLOv5-Flask/yolov5s.pt', source='local')

# POST 통신으로 들어오는 이미지를 저장하고 모델로 추론하는 과정
def save_image(file):
    file.save("YOLOv5-Flask/api_pic/req.jpg")

@app.route('/')
def web():
    return "team delevator start"


# check objects
# person, backpack, handbag, suitcase, dining table, cell phone, book


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        save_image(file) # 들어오는 이미지 저장
        # train_img = './temp/' + file.filename
        train_img = '"YOLOv5-Flask/api_pic/req.jpg"'
        temp = model(train_img)
        result = temp.pandas().xyxy[0]['name']
        check = True # check
        # answer = ""
        # for i in range(len(result)):
        #     if result[i] == "no-mask":
        #         check = False
        #         answer = "Detect"
        #         break
        
        # if check:
        #     answer = "Safe"

        # name = file.filename

        # res = {
        #     'answer' : answer,
        #     'name'   : name
        # }
        # os.remove('./temp/'+file.filename)

        # return res
        print(result)
        return result

if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)