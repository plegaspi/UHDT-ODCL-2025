def yolo_to_xyxy(box, img_w, img_h):
    """
    Converts YOLO format (center_x, center_y, width, height) to (x1, y1, x2, y2).

    Args:
        box (tuple): YOLO bbox (center_x, center_y, width, height), normalized (0-1).
        img_w (int): Width of the image.
        img_h (int): Height of the image.

    Returns:
        tuple: (x1, y1, x2, y2) pixel coordinates.
    """
    cx, cy, w, h = box
    x1 = (cx - w / 2) * img_w
    y1 = (cy - h / 2) * img_h
    x2 = (cx + w / 2) * img_w
    y2 = (cy + h / 2) * img_h
    return (x1, y1, x2, y2)

#this was chat, will have to reformat to better suit needs/use. Might use this to filter out "good detections"
def calculate_iou_yolo(box1, box2, image_width, image_height):
    """
    Calculates IoU (Intersection over Union) for YOLO bounding boxes.

    Args:
        box1 (tuple): YOLO bbox (center_x, center_y, width, height).
        box2 (tuple): YOLO bbox (center_x, center_y, width, height).
        image_width (int): Width of the image.
        image_height (int): Height of the image.

    Returns:
        float: IoU score (0 to 1).
    """
    # Convert YOLO boxes to (x1, y1, x2, y2)
    box1 = yolo_to_xyxy(box1, image_width, image_height)
    box2 = yolo_to_xyxy(box2, image_width, image_height)

    # Calculate Intersection Over Union (IoU)
    x1_intersect = max(box1[0], box2[0])
    y1_intersect = max(box1[1], box2[1])
    x2_intersect = min(box1[2], box2[2])
    y2_intersect = min(box1[3], box2[3])

    intersection_area = max(0, x2_intersect - x1_intersect) * max(0, y2_intersect - y1_intersect)

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = box1_area + box2_area - intersection_area

    return intersection_area / union_area if union_area > 0 else 0

def get_NoD_general(file_name):
    '''
    The plan is to loop through each line of a YOLO label file and get the number of targets, either detected or truth
    Ideally, each line should mean one target.
    This won't account for mistake detections so more math will have to be done.
    '''
    num_targets = 0
    with open(file_name) as true_file:
        for line in true_file:
            if type(int(line[0])) == int:
                num_targets +=1 #for every line in the "truth file", that should be one target

    return num_targets

def get_NoD_class(file_name, class_num):
    '''
    The plan is to loop through each line of a YOLO label file and get the number of targets for a certain class
    There should be a number associated to each object class (i.e. basketball is 1 or soemthing)
    This won't account for mistake detections so more math will have to be done.
    '''
    num_class_targets = 0
    with open(file_name) as true_file:
        for line in true_file:
            if int(line[0]) == class_num:
                num_class_targets +=1 
    
    return num_class_targets

#While there is chat's way to get the usual metrics, this function will try to get an accuracy for individual classes.
#ON SECOND THOUGHT, THIS FUNCTION MAY BE REDUNDANT. SINCE get_NoD_class EXISTS, A SEPARATE LOOP MAY BE ABLE TO DO THE JOB
def compare_classes(model, class_type, true_class_nums, detected_class_nums):
    '''
    The plan is to loop through each line of a YOLO file + some ground truth file and compare the classes overall.
    By overall, this means that it won't really keep track of the individual targets but rather just number of detected targets and targets that exist.

    true_class_nums refers to the actual number of targets that are the desired class
    detected_class_nums refers to the detected number of targets that are the desired class
    These can be (ideally) obtained using get_NoD_general.
    '''

    true_total = true_class_nums
    detected_total = 0
    
    for i in range(len(true_classes)):
        if (true_classes[i]==detected_classes[i]):
            positive_detects+=1 #if the class
            detections +=1
        else:
            detections +=1

    print(f"Overall true positives: {positive_detects/detections}")

#chat's way of getting the usual stats.
def calculate_metrics(TP, FP, FN):
    """
    Calculates precision, recall, and accuracy.

    Args:
        TP (int): True Positives
        FP (int): False Positives
        FN (int): False Negatives

    Returns:
        dict: Metrics {'Precision': float, 'Recall': float, 'Accuracy': float}
    """
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0

    return {'Precision': precision, 'Recall': recall, 'Accuracy': accuracy}
