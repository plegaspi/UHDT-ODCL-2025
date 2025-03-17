import os
import pandas as pd
import mpe_functions as mpe
#From Object_Detection import Object_Detection     From Obejct detection script

# Constants
IOU_THRESHOLD = 0.5
object_classes = ["person", "motorcycle", "car", "airplane", "bus", "boat", "stop_sign", "snowboard",
                  "umbrella", "sports_ball", "baseball_bat", "bed", "tennis_racket", "suitcase"]
labels_directory = "test_sample_folder"
image_directory = "test_image_folder"
detect_model = "Yolo_model_something"
config = "placeholder"
output_csv = "detection_results2.csv"

#data storage
detection_data = {cls: {"Detected": 0, "Ground Truth": 0, "True Positive": 0, "False Positive": 0, "Missed": 0} 
                  for cls in object_classes}

#loading annotations into array for later use
def load_annotations(annotation_path, image_w=1280, image_h=720):
    ground_truth = []
    if os.path.exists(annotation_path):
        with open(annotation_path, "r") as f:
            for line in f:
                values = line.split()
                class_id = int(values[0])
                bbox = list(map(float, values[1:]))  # YOLO format (cx, cy, w, h)
                xyxy_bbox = mpe.yolo_to_xyxy(bbox, image_w, image_h)  # Convert to (x1, y1, x2, y2)
                ground_truth.append({"class_id": class_id, "bbox": xyxy_bbox, "matched": False})
    return ground_truth

#need to figure this out (formatting)
'''def run_yolo_detection(image_path):
    results = Object_Detection(image_path, detect_model, config)
    return results'''

#good chunk of the logic stuff, again line 42 will depend on formatting of yolo output
def match_detections(yolo_results, ground_truth, image_w=1280, image_h=720):
    for detection in yolo_results:
        detected_class = int(detection[0])  # Extract class ID
        bbox = detection[1]  # Extract YOLO bbox (cx, cy, w, h)
        #print(bbox)
        xyxy_bbox = mpe.yolo_to_xyxy(bbox, image_w, image_h)  # Convert to (x1, y1, x2, y2)
        best_match = None
        best_iou = 0

        #compare with annotations
        for annotation in ground_truth:
            iou = mpe.calculate_iou_yolo(xyxy_bbox, annotation["bbox"], image_w, image_h)
            if iou > best_iou and iou >= IOU_THRESHOLD:
                best_iou = iou
                best_match = annotation

        #assign match
        if best_match and not best_match["matched"]:
            best_match["matched"] = True  # Mark annotation as matched
            if detected_class == best_match["class_id"]:
                detection_data[object_classes[detected_class]]["True Positive"] += 1
            else:
                detection_data[object_classes[detected_class]]["False Positive"] += 1
        else:
            detection_data[object_classes[detected_class]]["False Positive"] += 1

    #count missed detections
    for annotation in ground_truth:
        if not annotation["matched"]:
            detection_data[object_classes[annotation["class_id"]]]["Missed"] += 1

#main loop (need to test with actual folders) - but at least we know functions work with single files
'''for image_file in os.listdir(image_directory):
    if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(image_directory, image_file)
        annotation_path = os.path.join(labels_directory, image_file.replace(".jpg", ".txt").replace(".png", ".txt"))

        # Load annotations and run detection
        ground_truth = load_annotations(annotation_path)
        yolo_results = run_yolo_detection(image_path)

        # Match detections and compute stats
        match_detections(yolo_results, ground_truth)
'''

#TEST INPUTS
gt1 = load_annotations("0HC3FY0JZYCK_jpg.rf.3a4ac6d828de0b66e5d7d1e9c16d989d.txt")
test_yoloresults = [[0, (0.86015625, 0.4828125, 0.2109375, 0.1453125)],
                    [5, (0.146875, 0.46484375, 0.29375, 0.7578125)],
                    [3, (0.609375, 0.5234375, 0.765625, 0.653125)]]

match_detections(test_yoloresults, gt1, image_w=1280, image_h=720)
print(detection_data)

#math for metrics
for cls_name in object_classes:
    TP = detection_data[cls_name]["True Positive"]
    FP = detection_data[cls_name]["False Positive"]
    FN = detection_data[cls_name]["Missed"]
    metrics = mpe.calculate_metrics(TP, FP, FN)

    detection_data[cls_name]["Precision"] = metrics["Precision"]
    detection_data[cls_name]["Recall"] = metrics["Recall"]
    detection_data[cls_name]["Accuracy"] = metrics["Accuracy"]

#doing math for an overall/total metrics
df = pd.DataFrame.from_dict(detection_data, orient="index")
total_TP = df["True Positive"].sum()
total_FP = df["False Positive"].sum()
total_FN = df["Missed"].sum()

overall_precision = total_TP / (total_TP + total_FP) if (total_TP + total_FP) > 0 else 0
overall_recall = total_TP / (total_TP + total_FN) if (total_TP + total_FN) > 0 else 0

#attach total stats to the datafram for csv
total_row = df.sum(numeric_only=True)  #sum all numerical columns
total_row.name = "Total"  #label the total row
total_row["Precision"] = overall_precision
total_row["Recall"] = overall_recall
total_row["Accuracy"] = "-"  #TODO

df = df.append(total_row)

df.to_csv(output_csv, index=True)

print(f"Detection results saved to {output_csv}")
