
#this was chat
def calculate_iou(box1, box2):
    """
    Calculates the Intersection over Union (IoU) of two bounding boxes.
    Essentially, this will tell us how close the detected area is to where the item
    actually is

    Args:
        box1 (tuple): (x1, y1, x2, y2) coordinates of the first box.
        box2 (tuple): (x1, y1, x2, y2) coordinates of the second box.

    Returns:
        float: The IoU score, ranging from 0 to 1.
    """
    x1_intersect = max(box1[0], box2[0])
    y1_intersect = max(box1[1], box2[1])
    x2_intersect = min(box1[2], box2[2])
    y2_intersect = min(box1[3], box2[3])

    intersection_area = max(0, x2_intersect - x1_intersect) * max(0, y2_intersect - y1_intersect)

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = box1_area + box2_area - intersection_area

    iou = intersection_area / union_area if union_area > 0 else 0
    return iou

# Example usage:
box_a = (50, 40, 100, 120)
box_b = (50, 40, 100, 120)

iou_score = calculate_iou(box_a, box_b)
print(f"The IoU score is: {iou_score}")


#There's probably a better way to do this but just to get something down
def compare_classes(true_file_name, detected_file_name):
    '''
    The plan is to loop through each line of a YOLO file + some ground truth file and compare the classes.
    You will need some type of read() function to open text files.
    From there, we can tally up things and output some numbers
    '''
    detections = 0
    positive_detects = 0

    true_classes = []
    detected_classes = []
    with open('name of file.txt') as true_file:
        for line in true_file:
            true_classes.append(line[1])

    for i in range(len(true_classes)):
        if (true_classes[i]==detected_classes[i]):
            positive_detects+=1
            detections +=1
        else:
            detections +=1

    print(f"true positives: {positive_detects/detections}")
