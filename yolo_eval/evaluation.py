import supervision as sv
import cv2
import os
import glob
from ultralytics import YOLO
import numpy as np


folder_path = "yolo-eval/test_imgs"
img_extension = ".jpg"
model = YOLO("yolov8n.pt")

image_paths = glob.glob(f"{folder_path}/*{img_extension}")
for image_path in image_paths:
    image = cv2.imread(image_path)
    results = model(image)[0]
    detections = sv.Detections.from_ultralytics(results)
    bounding_box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    labels = [model.model.names[class_id] for class_id in detections.class_id]
    annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
    stacked_image = np.vstack([image, annotated_image])
    cv2.imshow(image_path,stacked_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



