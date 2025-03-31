import os
import pandas as pd
import mpe_functions as mpe
import random
#From Object_Detection import Object_Detection     From Obejct detection script

# Constants
IOU_THRESHOLD = 0.5
object_classes = ["person", "motorcycle", "car", "airplane", "bus", "boat", "stop_sign", "snowboard",
                  "umbrella", "sports_ball", "baseball_bat", "bed", "tennis_racket", "suitcase"]
labels_directory = "labels_MPE_script_testing"
image_directory = "test_image_folder"
detect_model = "Yolo_model_something"
config = "placeholder"
run_number = input("test run #: ")
detect_output_csv = f"detection_results_{run_number}.csv"
classify_output_csv = f"classification_results_{run_number}.csv"

#data storage
detection_data = {cls: {"Ground Truth Number Detections": 0, "Detected": 0 , "True Positive": 0, "False Positive": 0, "Missed": 0} for cls in object_classes}
classified_data = {cls: {f"d_{objclass}":0 for objclass in object_classes} for cls in object_classes}
#print(classified_data)

raw_tp = 0
raw_fn = 0
raw_gt = 0

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
    #assert all("matched" in gt for gt in ground_truth)
    return ground_truth
def gen_test_yoloresults(annotation_path):  #making this function so i can maybe adjust and simulate yolo reults without actually running yolo on actual pics (need some desirable pics)
    sim_yolo_outputs = []
    if os.path.exists(annotation_path):
        with open(annotation_path, "r") as f:
            for line in f:
                line_buff = []
                values = line.split()
                class_id = int(values[0])#random.randint(0,1) #added rng to simulate "detections"
                bbox = list(map(float, values[1:]))  # YOLO format (cx, cy, w, h)
                #bbox = [num + random.uniform(0,0.13) for num in bbox ]
                line_buff.append(class_id)
                line_buff.append(bbox)
                sim_yolo_outputs.append(line_buff)
    return sim_yolo_outputs

#need to figure this out (formatting)
'''def run_yolo_detection(image_path):
    results = Object_Detection(image_path, detect_model, config)
    return results'''

#good chunk of the logic stuff, again line 42 will depend on formatting of yolo output
def match_detections(yolo_results, ground_truth, image_w=1280, image_h=720):
    global raw_tp, raw_fn, raw_gt
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

            ######### if object was detected update confusion/misclassification count ####################
            true_class = object_classes[best_match["class_id"]]
            pred_class = f'd_{object_classes[detected_class]}'
            classified_data[true_class][pred_class] += 1

            ######### update the metrics ###############################
            if detected_class == best_match["class_id"]:
                detection_data[object_classes[detected_class]]["True Positive"] += 1
                raw_tp+=1
            else:
                detection_data[object_classes[detected_class]]["False Positive"] += 1
            detection_data[object_classes[detected_class]]["Detected"] += 1 #increment the detected value since this will count as a detection

    #count missed detections
    for annotation in ground_truth:
        print(annotation)
        class_name = object_classes[annotation["class_id"]]
        detection_data[class_name]["Ground Truth Number Detections"] += 1
        raw_gt += 1  # <--- Count total GTs
        if not annotation["matched"]:
            detection_data[class_name]["Missed"] += 1
            raw_fn += 1  # <--- Count missed



###############TEST INPUTS#####################

#testing load annotations/generate test yolo outputs functions (works)

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
for file in os.listdir(labels_directory):
    annotation_path = os.path.join(labels_directory, file)
    ground_truth = load_annotations(annotation_path)
    yolo_results = gen_test_yoloresults(annotation_path)
    
    print(f"{file}: GT count = {len(ground_truth)}, YOLO results = {len(yolo_results)}")

    match_detections(yolo_results, ground_truth)
#match_detections(sim_test_yolo_results, groundtruth_labels, image_w=1280, image_h=720)
print(detection_data)

#math for metrics
for cls_name in object_classes:
    TP = detection_data[cls_name]["True Positive"]
    FP = detection_data[cls_name]["False Positive"]
    FN = detection_data[cls_name]["Missed"]
    metrics = mpe.calculate_metrics(TP, FP, FN)

    detection_data[cls_name]["Precision"] = metrics["Precision"]
    detection_data[cls_name]["Recall"] = metrics["Recall"]
    detection_data[cls_name]["Class Accuracy"] = metrics["Accuracy"]

#doing math for an overall/total metrics
df = pd.DataFrame.from_dict(detection_data, orient="index")
total_detect = df["Detected"].sum()
total_GT = df["Ground Truth Number Detections"].sum()
total_TP = df["True Positive"].sum()
total_FP = df["False Positive"].sum()
total_FN = df["Missed"].sum()

overall_precision = total_TP / (total_TP + total_FP) if (total_TP + total_FP) > 0 else 0
overall_recall = total_TP / (total_TP + total_FN) if (total_TP + total_FN) > 0 else 0
#overall_class_accuracy = total_TP/total_detect   #omitted since this is actually the same as precision
overall_detect_accuracy = total_detect/total_GT

#attach total stats to the datafram for csv
total_row = df.sum(numeric_only=True)  #sum all numerical columns

total_row.name = "Total"  #label the total row
total_row["Precision"] = round(overall_precision,3)
total_row["Recall"] = round(overall_recall,3)
total_row["Detect Accuracy"] = round(overall_detect_accuracy*100,3) #multiply 100 for percent. Remove if unnecessary

print("\n=== RAW DEBUG STATS ===")
print(f"Raw TP: {raw_tp}")
print(f"Raw FN: {raw_fn}")
print(f"Raw GT: {raw_gt}")
print(f"TP + FN == GT? {raw_tp + raw_fn == raw_gt}")

#turn the dictionaries into csv files.
df = pd.concat([df, total_row.to_frame().T])
df.to_csv(detect_output_csv, index=True)
print(f"Detection results saved to {detect_output_csv}")

df2 = pd.DataFrame.from_dict(classified_data, orient="index")
df2.to_csv(classify_output_csv, index=True)
print(f"Classification results saved to {classify_output_csv}")
