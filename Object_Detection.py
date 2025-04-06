from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction, get_prediction
from sahi.postprocess.combine import (
    GreedyNMMPostprocess,
    LSNMSPostprocess,
    NMMPostprocess,
    NMSPostprocess,
    PostprocessPredictions,
)
from sahi.utils.cv import visualize_object_predictions
import os
import cv2
from PIL import Image

def Object_Detection(image, detection_model, sahi_config, sahi_single_prediction_postprocess_config):
    if sahi_config["slice"]:
        result = get_sliced_prediction(
            image,
            detection_model,
            slice_height= sahi_config["slice_height"],
            slice_width= sahi_config["slice_width"],
            overlap_height_ratio= sahi_config["overlap_height_ratio"],
            overlap_width_ratio= sahi_config["overlap_width_ratio"],
            perform_standard_pred= sahi_config["perform_standard_pred"],
            postprocess_match_metric= sahi_config["postprocess_match_metric"],
            postprocess_match_threshold= sahi_config["postprocess_match_threshold"],
            postprocess_class_agnostic=True
        )
    else:
        postprocess_types = [None, GreedyNMMPostprocess, LSNMSPostprocess, NMMPostprocess, NMSPostprocess, PostprocessPredictions]
        postprocess_type = None
        if sahi_single_prediction_postprocess_config["postprocess_type"] != 0:
            postprocess_type = postprocess_types[sahi_single_prediction_postprocess_config["postprocess_type"]](
                match_threshold = sahi_single_prediction_postprocess_config["match_threshold"],
                match_metric = sahi_single_prediction_postprocess_config["match_metric"],
                class_agnostic = sahi_single_prediction_postprocess_config["class_agnostic"],
            )
        result = get_prediction(image=image, detection_model=detection_model, postprocess=postprocess_type)
        
    return result

def adjust_bbox(bb, padding, img_width, img_height):
    x_min, y_min, x_max, y_max = bb
    while True:
        new_x_min = max(x_min - padding, 0)
        new_y_min = max(y_min - padding, 0)
        new_x_max = min(x_max + padding, img_width)
        new_y_max = min(y_max + padding, img_height)

        if new_x_min == x_min and new_y_min == y_min and new_x_max == x_max and new_y_max == y_max:
            break

        x_min, y_min, x_max, y_max = new_x_min, new_y_min, new_x_max, new_y_max
        padding -= 1

    return (new_x_min, new_y_min, new_x_max, new_y_max)

if __name__ == "__main__":
    image_name = ""
    sahi_config = {
        "slice": False,
        "slice_height": 640,
        "slice_width": 640,
        "overlap_height_ratio": 0.11,
        "overlap_width_ratio": 0.11,
        "perform_standard_pred": False,
        "postprocess_match_metric": "IOU",
        "postprocess_match_threshold": 0.3
    }

    sahi_single_prediction_postprocess_config = {
        "postprocess_type": "NMMPostprocess",
        "match_threshold": 0.2,
        "match_metric": "IOU",
        "class_agnostic": True
    }