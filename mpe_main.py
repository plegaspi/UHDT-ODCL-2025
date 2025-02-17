import os
import mpe_functions as mpe
object_classes = ["person", "motorcycle", "car", "airplane", "bus", "boat", "stop_sign", "snowboard", "umbrella", "sports_ball", "baseball_bat", "bed", "tennis_racket", "suitcase"]

directory = "test_sample_folder" #this directory should be holding the annotation txt files.

# data = panda csv (for raw data)

# Raw YOLO Data
# [classification, confidence_score, bounding_box] 

# Iterate over files in directory
for file in os.listdir(directory):
    # Open file
    with open(os.path.join(directory, file)) as f:

        #print(f"Content of '{f.name}'")
        # Read content of file
        #print(f.read())
        print(f'the # of {object_classes[0]} for {f.name} is {mpe.get_NoD_class(f.name,0)}')
        object_person = 0 
        object_motorcylce=0

        if(object_classes == "person" ):
            object_person+=1
        elif (object_classes == "motorcycle" ):
            object_motorcylce+=1

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
# 1. Loop through annotations, get the overall total number of desired targets (ideally one line = one target)
# 2. (May be in parallel with step 1) Loop through annotations, get the total number of targets for each class

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

