# Parameters
# Folder directory with annotations and images
# Path to yolo model of interest
# Optional: CSV File(s) of results


# Data to Collect
# - Number of detections (Per Image and Class)
# - Number of true positive detections (Per Image and Class)
# - Number of false positive detections (Per Image and Per Class)
# - Number of missed detections (Per Image and Per Class)
# - Precision
# - Recall
# - Commonly confused classifications (can be a list of classifications)


# c = done, p = in progress, no label = haven't touched

# Initialization
# 1. Loop through annotations, get the overall total number of desired targets (ideally one line = one target) c
# 2. (May be in parallel with step 1) Loop through annotations, get the total number of targets for each class p

# Loop Info
# 1. Get all images and annotations in folder directory (os.listdir or glob) c
# 2. Loop through images (every image) c
#    - Run against YOLO c
#    - Compare results against annotation file (annotation file has the same name as image but ends in txt) c
# 3. Output into console and as csv files p

# Loop Steps/Calculations (BIG DOG)
# 3. Compare the outputs of the yolo model with the annotations ---> How to determine which ideal target gets compared to detected target??? 
#    - Get the IOU scores of the bounding boxes c
#    - Given a certain IOU threshold, if the detected target class matches the desired target class add to a counter of true positives. c
#       If detected target has matching bounding boxes with incorrect classification
#       add to false positives. If # of detected targets < # of desired targets, take 
#       difference and use as missed detections. Do other math for metrics (i.e. precision, recall, mAP)
# 4. Figure out way to quanitfy commonly confused classifications and store results. p
#    Misclassifications
#    basket_ball:dog, car:bus
# 5. Store the results (the metric calculations) and output all metrics at the end. p

from Object_Detection import Object_Detection
import os
import mpe_functions as mpe
import pandas as pd
object_classes = ["person", "motorcycle", "car", "airplane", "bus", "boat", "stop_sign", "snowboard", "umbrella", "sports_ball", "baseball_bat", "bed", "tennis_racket", "suitcase"]

labels_directory = "test_sample_folder" #this directory should be holding the annotation txt files.
image_directory = "test_image_folder"
detect_model = "Yolo_model_something"
config = "placeholder"

output_csv = f"{detect_model}_model_results.csv"

IoU_thresh = 0.5
#{
# slice_height: 600,
#  overlap_height_ratio: 60
# }
# data = panda csv (for raw data)

# Raw YOLO Data
# [classification, confidence_score, bounding_box] probably what the "results" variable is gonna hold. IF not, can adjust it to do so or something.

detection_data = {obj: {"detected":0, "actual":0, "true positive":0, "false positive":0, "missed": 0, "precision": 0, "recall":0, "accuracy":0} for obj in object_classes} #dictionary to hold data fro each obejct

total_targets = mpe.get_NoD_general(labels_directory) if os.path.exists(labels_directory) else 0 #get total total number of actual targets

#YOLO-ing - loop through the photos 
for image_file in os.listdir(image_directory): # i.e. image_file = dillonbigyeah.jpg
    #look for image files (i.e. jpg and jpegs) and get the path to image
    if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(image_directory, image_file)
        annotation_file_path = os.path.join(labels_directory, image_file.replace(".jpg", ".txt").replace(".png", ".txt")) # get the annotation file for the photo (should eb same name as image)

        yolo_results = Object_Detection(image_path,detect_model,config) #[classification, confidence_score, bounding_box], use obejct detection script that was already made #TODO should there be a default config???
        #detected_classes = [int(result[0]) for result in yolo_results] # not sure if results will be a single result or a collection of results
        
        #while looping, get the gorund truth data of the corresponding image/photo
        ground_truth = []
        image_w, image_h = 1280, 720  # FILLER --> replace with actual image dimensions if available
        if os.path.exists(annotation_file_path):
            with open(annotation_file_path, "r") as f:
                for line in f:
                    values = line.split() #turn the numbers on each line into an array
                    class_id = int(values[0])
                    bbox = tuple(map(float, values[1:]))  # turn bounding box values (cx cy h w) into a list, MAY BE ISSUE SINCE yolo_yo_xyxy might only take tuple #TODO consider fix
                    xyxy_bbox = mpe.yolo_to_xyxy(bbox, image_w, image_h)  
                    ground_truth.append({"class_id": class_id, "bbox": xyxy_bbox, "matched": False}) #bbox are xy coords of box
                    detection_data[object_classes[class_id]]["actual"] += 1  # Update per-class count

        for detection in yolo_results: #collection of targets, so far each target:
            detected_class = int(detection[0]) #get class id from the result
            bbox = mpe.yolo_to_xyxy(detection[2],image_w,image_h) #get the bounding box in terms of x and y corner coords

            #holders that will be updated as the image is compared to each annotation/annotated target
            best_match = None
            best_iou = 0

            #compare image with each annotation
            for annotation in ground_truth:
                iou_score = mpe.calculate_iou_yolo(bbox,annotation["bbox"], image_w , image_h)
                if iou_score > best_iou and iou_score >= IoU_thresh:
                    best_iou = iou_score #update best iou score
                    best_match = annotation # where annotation is a dictionary representing a line in the annotation file 
            
            #assign image to annotation if a valid match
            if best_match and not best_match["matched"]:
                best_match["matched"] = True
                if detected_class == best_match["class_id"]:
                    detection_data[object_classes[detected_class]]["true positive"] += 1
                else:
                    detection_data[object_classes[detected_class]]["false positive"] += 1
            else:
                detection_data[object_classes[detected_class]]["false positive"] += 1

        for annotation in ground_truth:
            if not annotation["matched"]:
                detection_data[object_classes[annotation["class_id"]]]["missed"] += 1

#do the math stuff and store in data dictionary
for class_name in object_classes:
    #extract the number of true positives, false positives, and missed detections for each object class
    TP = object_classes[class_name]["true positive"]
    FP = object_classes[class_name]["false positive"]
    MI = object_classes[class_name]["missed"]

    metrics = mpe.calculate_metrics(TP,FP,MI) #this retruns a dictionary with precision, recall, and missed detects

    #store the calculated metrics into data dictionary
    detection_data[class_name]["precision"] = metrics["precision"]
    detection_data[class_name]["recall"] = metrics["recall"]
    detection_data[class_name]["accuracy"] = metrics["accuracy"]


#output the dictionary as csv using pandas
df = pd.DataFrame.from_dict(detection_data, orient="index")
df.to_csv(output_csv, index=True)