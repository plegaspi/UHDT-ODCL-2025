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


# Initialization
# 1. Loop through annotations, get the overall total number of desired targets (ideally one line = one target) c
# 2. (May be in parallel with step 1) Loop through annotations, get the total number of targets for each class c

# Loop Info
# 1. Get all images and annotations in folder directory (os.listdir or glob)
# 2. Loop through images (every image)
#    - Run against YOLO
#    - Compare results against annotation file (annotation file has the same name as image but ends in txt)\
# 3. Output into console and as csv files

# Loop Steps/Calculations (BIG DOG)
# 3. Compare the outputs of the yolo model with the annotations ---> How to determine which ideal target gets compared to detected target???
#    - Get the IOU scores of the bounding boxes
#    - Given a certain IOU threshold, if the detected target class matches the desired target class add to a counter of true positives. 
#       If detected target has matching bounding boxes with incorrect classification
#       add to false positives. If # of detected targets < # of desired targets, take 
#       difference and use as missed detections. Do other math for metrics (i.e. precision, recall, mAP)
# 4. Figure out way to quanitfy commonly confused classifications and store results.
#    Misclassifications
#    basket_ball:dog, car:bus
# 5. Store the results (the metric calculations) and output all metrics at the end.

from Object_Detection import Object_Detection
import os
import mpe_functions as mpe
object_classes = ["person", "motorcycle", "car", "airplane", "bus", "boat", "stop_sign", "snowboard", "umbrella", "sports_ball", "baseball_bat", "bed", "tennis_racket", "suitcase"]

labels_directory = "test_sample_folder" #this directory should be holding the annotation txt files.
image_directory = "test_image_folder"
detect_model = "Yolo_model_something"
config = "placeholder"
#{
# slice_height: 600,
#  overlap_height_ratio: 60
# }
# data = panda csv (for raw data)

# Raw YOLO Data
# [classification, confidence_score, bounding_box] probably what the "results" variable is gonna hold. IF not, can adjust it to do so or something.

total_targets = mpe.get_NoD_general(labels_directory)
num_targets = {}

#INITIALIZATION
# Iterate over files in directory
for file in os.listdir(labels_directory):
    # Open file
    with open(os.path.join(labels_directory, file)) as f:
        for line in f:
            num_targets[object_classes[int(line[0])]] = num_targets.get(object_classes[int(line[0])], 0) + 1

#YOLO-ing
for image_file in os.listdir(image_directory):
    #check for photos (i.e. jpg and jpegs) and get the path to image
    if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(image_directory, image_file)
        annotation_path = os.path.join(labels_directory, image_file.replace(".jpg", ".txt").replace(".png", ".txt")) # get the annotation file for the photo (should eb same name as image)

        results = Object_Detection(image_path,detect_model,config) #use obejct detection script that was already made #TODO should there be a default config???
        


