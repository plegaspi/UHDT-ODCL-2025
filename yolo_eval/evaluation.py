import supervision as sv
import cv2
import os
import glob
from ultralytics import YOLO
import numpy as np


folder_path = "yolo_eval/test_imgs" # Enter the file path for the folder with images. Not the
                                    # folder path with the data.yaml file.
img_extension = ".jpg"
model = YOLO("yolov8n.pt") # Enter the model name that you are assigned. <model_name>.pt
                           # E.g.) yolov9-t.pt

image_paths = glob.glob(f"{folder_path}/*{img_extension}")

def callback(image_slice: np.ndarray) -> sv.Detections:
    result = model(image_slice)[0]
    return sv.Detections.from_ultralytics(result)

for image_path in image_paths:
    image = cv2.imread(image_path)
    orig_image = np.array(image, copy=True)
    results = model(image)[0]
    slicer = sv.InferenceSlicer(slice_wh=(640, 640),
                                overlap_ratio_wh=(0.11, 0.11),
                                iou_threshold=0.3,
                                callback = callback,
                                thread_workers=10
                                )
    detections = slicer(image)
    bounding_box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    labels = [model.model.names[class_id] for class_id in detections.class_id]
    annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
    stacked_image = np.vstack([orig_image, annotated_image])
    cv2.imshow(image_path,stacked_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



