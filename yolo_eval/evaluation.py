import supervision as sv
import cv2
import os
import glob
from ultralytics import YOLO
import numpy as np
from pathlib import Path
import shutil


folder_path = "test-set" # Enter the file path for the folder with images. Not the
                                    # folder path with the data.yaml file.
img_extension = ".jpg"
model = YOLO("yolov8n.pt") # Enter the model name that you are assigned. <model_name>.pt
                           # E.g.) yolov9-t.pt

image_paths = glob.glob(f"{folder_path}/*{img_extension}")

def callback(image_slice: np.ndarray) -> sv.Detections:
    result = model.predict(image_slice)[0]
    return sv.Detections.from_ultralytics(result).with_nms(0.01)

test_folder_dir_path = "yolo_eval/test_results"
shutil.rmtree(test_folder_dir_path, ignore_errors=True)
os.makedirs(test_folder_dir_path, exist_ok=True)
for image_path in image_paths:
    image = cv2.imread(image_path)
    orig_image = np.array(image, copy=True)
    results = model(image)[0]
    #slicer = sv.InferenceSlicer(slice_wh=(640, 640),
    #                            overlap_ratio_wh=(0.1, 0.1),
    #                            iou_threshold=0.001,
    #                            callback = callback,
    #                            thread_workers=10,
    #                            )
    detections = callback(image)#(image)
    bounding_box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    labels = [model.model.names[class_id] for class_id in detections.class_id]
    annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
    #stacked_image = np.vstack([orig_image, annotated_image])
    #cv2.imshow(image_path, orig_image)
    #cv2.imshow(image_path,annotated_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    img_save_path = os.path.join(test_folder_dir_path, Path(image_path).name)
    print(f"Saving to {img_save_path}")
    cv2.imwrite(img_save_path, annotated_image)


