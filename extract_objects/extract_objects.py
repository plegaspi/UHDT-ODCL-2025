import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO, SAM
import supervision as sv

from annotations import *

def adjust_bbox(base_img, bb, padding = 10):
    img_height, img_width, img_channels = base_img.shape
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

def extract_object_sv_test(base_img, yolo_annotation, padding=0):
    model = SAM("sam2_b.pt") 
    object_class, object_center_x, object_center_y, object_width, object_height = extract_yolo_class_and_coords(yolo_annotation)
    input_box = convert_yolo_coords_to_pixel_coords(base_img, object_center_x, object_center_y, object_width, object_height)
    input_box = adjust_bbox(base_img, input_box, padding)
    res = model(base_img,bboxes=input_box, points=[object_center_x, object_center_y], labels=[1])
    return res

def extract_object(base_img, yolo_annotation, padding=0):
    model = SAM("sam2_b.pt") 
    object_class_id, object_center_x, object_center_y, object_width, object_height = extract_yolo_class_and_coords(yolo_annotation)
    input_box = convert_yolo_coords_to_pixel_coords(base_img, object_center_x, object_center_y, object_width, object_height)
    res = model(base_img,bboxes=input_box, points=[object_center_x, object_center_y], labels=[1])
    
    for r in res:
        img = np.copy(r.orig_img)

        # Iterate each object contour 
        for ci, c in enumerate(r):
            label = c.names[c.boxes.cls.tolist().pop()]

            b_mask = np.zeros(img.shape[:2], np.uint8)
            # Create contour mask 
            contour = c.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
            _ = cv2.drawContours(b_mask, [contour], -1, (255, 255, 255), cv2.FILLED)
            isolated = np.dstack([img, b_mask])
            x1, y1, x2, y2 = c.boxes.xyxy.cpu().numpy().squeeze().astype(np.int32)
            iso_crop = isolated[y1:y2, x1:x2]
            return iso_crop
        

if __name__ == "__main__":
    img = cv2.imread("Mannequins detection.v1i.yolov8/test/images/img-146-_jpg.rf.f80713a2c6a0e4c5b224ccf163e97769.jpg")
    yolo_annotation = "0 0.47003154574132494 0.49273447820343463 0.27129337539432175 0.9722589167767504"
    result = extract_object(img, yolo_annotation)
    cv2.imwrite('bruh.png', result)