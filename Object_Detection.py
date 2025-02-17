from sahi.predict import get_sliced_prediction, get_prediction

###
# config = {
#   slice_height: 600,
#   overlap_height_ratio: 60
# }
#####

def Object_Detection(image, detection_model, config):
    if config["slice"]:
        result = get_sliced_prediction(
            image,
            detection_model,
            slice_height= config["slice_height"],
            slice_width= config["slice_width"],
            overlap_height_ratio= config["overlap_height_ratio"],
            overlap_width_ratio= config["overlap_width_ratio"],
            perform_standard_pred= config["perform_standard_pred"],
            postprocess_match_metric= config["postprocess_match_metric"],
            postprocess_match_threshold= config["postprocess_match_threshold"]
        )
    else:
        result = get_prediction(image=image, detection_model=detection_model)
    return result
# This spits out the result that we need to analyze with respect to the desired result
    

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