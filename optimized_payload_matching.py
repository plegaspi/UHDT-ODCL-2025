from Classes import Detection, Target


def optimized_payload_matching(targets, detections):
    """
    Receives a list of targets (as Target Objects) and detections (as detection objects)

    ###################
    # Example Usage:  #
    ###################
    targets = ["sports_ball", "baseball_bat", "car", "airplane"]

    detections = [<Detection>, <Detection>, <Detection>, <Detection>, <Detection>, <Detection>]

    optimized_payload_matching(targets, detections)

    
    #########################
    # Detection Object Info #
    #########################

    Each detection object has the following properties:
    1) classification, 
    2) confidences,
    3) coordinates,
    4) original_image,
    5) cropped_image

    classification is an array of strings describing classifications in order of descending confidence:
    classifications = ["sports_ball", "baseball_bat", "car", "airplane"]

    confidences is an array of floats describing confidence scores in order of descending confidence
    confidences = [0.99, 0.01, 0.00, 0.00]

    coordinates is a tuple containing the detection's longitutde and latitude
    confidence = (longitude, latitude)

    original_image is a Numpy array or PIL image (TBD) containing the original image containing
    the detection

    cropped_image is a Numpy array or PIL image (TBD) containing a cropped image with only
    the detection

    #########################
    # Target Object Info #
    #########################


    ##########
    # Output #
    ##########
    The function should output a list of Target objects. These should be the list of Target objects
    that were originally passed in to the function as an argument but with their coordinates and
    number_of_payloads set.

    return [<Target>, <Target>, <Target>, <Target>]

    """
