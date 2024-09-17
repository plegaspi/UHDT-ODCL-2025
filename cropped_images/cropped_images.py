from ultralytics import YOLO
import numpy as np
import cv2
import os
import sys
from sahi.utils.yolov8 import download_yolov8s_model
from sahi import AutoDetectionModel
from sahi.utils.cv import read_image
from sahi.utils.file import download_from_url
from sahi.predict import get_prediction, get_sliced_prediction, predict
from pathlib import Path
from PIL import Image
import string
import random

# Modify base_dir to be the file path to the dataset
base_dir = os.path.join("cropped_images", "datasets", "pre-processed", "3-8-24 DJI Images")
# Modify padding to change the amount of padding (in px) around the cropped image of the target
padding = 10
model_path_base = os.path.join("cropped_images","weights")
model_name = "nanotarget1.pt"
model_suffix = os.path.splitext(model_name)[0]
model_path = os.path.join(model_path_base, model_name)
base_dir_name = os.path.split(base_dir)[1]

print(model_path)
detection_model = AutoDetectionModel.from_pretrained(
    model_type='yolov8',
    model_path=model_path,
    confidence_threshold=0.7,
    device="cuda:0"
)

def ObjectDetection(image):
    image = Image.open(image)
    result = get_sliced_prediction(
            image,
            detection_model,
            slice_height=640,
            slice_width=640,
            overlap_height_ratio=0.11,
            overlap_width_ratio=0.11,
            perform_standard_pred=False,
            postprocess_match_metric='IOU',
            postprocess_match_threshold=0.3
        )
    return result

def adjust_bbox(bb, padding, img_width, img_height):
    x_min, y_min, x_max, y_max = bb
    while True:
        new_x_min = max(x_min - padding, 0)
        new_y_min = max(y_min - padding, 0)
        new_x_max = min(x_max + padding, img_width)
        new_y_max = min(y_max + padding, img_height)

        if new_x_min == x_min and new_y_min == y_min and new_x_max == x_max and new_y_max == y_max:
            break

        x_min, y_min, x_max, y_max = new_x_min, new_y_min, new_x_max, new_y_max
        padding -= 1

    return (new_x_min, new_y_min, new_x_max, new_y_max)



if padding:
    count = 0
    for image in os.listdir(base_dir):
        img = Image.open(os.path.join(base_dir, image))
        img_width, img_height = img.size
        result = ObjectDetection(os.path.join(base_dir, image))
        print(result.object_prediction_list)
        if len(result.object_prediction_list) > 0:
            for prediction in result.object_prediction_list:
                BB = prediction.bbox.to_voc_bbox()
                print(BB)
                adjusted_BB = adjust_bbox(BB, padding, img_width, img_height)
                name, fext = os.path.splitext(f"{image}")
                cropped = img.crop(adjusted_BB)
                output_dir = os.path.join("cropped_images", "datasets", "processed", f"{base_dir_name}-{padding}-{model_suffix}")
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                cropped.save(os.path.join(output_dir,f"{name}-cropped{count}.jpg"))
                count += 1
    print(f"Detected {count} targets")

