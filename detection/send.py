import requests
import os
import json

def send_data(url):
    path_dir = 'YOLOv5-Flask/data/images/bus.jpg'
    # file_list = os.listdir(path_dir)
    # for name in file_list:
    #     files = {
       
    #         'file':open('YOLOv5-Flask/data/images/' + name, 'rb')
    #     }

    upload = {'file': path_dir}

    res = requests.post(url, files = upload)

    # files = {'file':open(path_dir)}
    # res = requests.post(url,files=files)
        #name = res['name']
    res_json = res.json()
    # if res_json['answer'] == "Detect":
    #     os.system("mv YOLOv5-Flask/data/images/" + name + " /root/web" )
    # else:
    #     os.system("rm -f YOLOv5-Flask/data/images/"+ name)
    # return "Done"
    return

url = "http://localhost/predict"
print(send_data(url))