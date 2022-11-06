import requests
import os
import json


def file_name_test():
    path_dir1 = 'YOLOv5-Flask/data/images/'
    file_list1 = os.listdir(path_dir1)
    for name in file_list1:
        print(name)

file_name_test()