##########
# Utils #
#########
import cv2
import os
from PIL import Image
import time
import shutil
import numpy as np
import math
from datetime import datetime
from sahi import AutoDetectionModel
import logging
import json


##########
# Config #
##########
from Config import Config
from classes import Target


###################
# ODCL Algorithms #
###################
from Object_Detection import Object_Detection, adjust_bbox
from Georeferencing import Georeference, haversine, extractMetadata
from OPM2 import Optimized_Payload_Matching, create_waypoint_file, calculate_default_drop_coordinates, sort_coordinates, get_midpoint

#####################
# Payload Delivery  #
#####################
from payloadDelivery import deliveryScript


#################
# Configuration #
#################
import argparse
# Argument parser
parser = argparse.ArgumentParser(description="Run ODCL2 with optional flight-testing config.")
parser.add_argument('--flight-testing', action='store_true', help="Use flight-testing configuration file")
args = parser.parse_args()

# Config selection
config_path = "/home/uhdt/UHDT-ODCL-2025/config/config.yaml"

if args.flight_testing:
    config_path = "/home/uhdt/UHDT-ODCL-2025/config/flight-testing.yaml"

config = Config(config_path)
targets = config.targets
num_photos = config.params["num_photos"]
mode = config.params["mode"]
debug = config.params["debug"]



###################
# Watch Directory #
###################
watch_dir_path = config.watch_dir_path
watch_delay = 2
waypoint_file_path = config.params["waypoint_file_path"]

##########
# Camera #
##########
#config = Config("config/config.yaml")
load_camera_config = config.params["camera"]["load_config"]
load_ext_camera_config = config.params["camera"]["load_ext_config"]
camera_config_file = config.params["camera"]["ext_config"]
camera_yaml_config= config.params["camera"]["config"]

preset = None

"""
if load_ext_camera_config:
    with open(camera_config_file) as f:
        camera_config = json.load(f)
        preset = {}
        for key, value in camera_config.items():
            preset[key] = value
else:
    preset = {key: value for key, value in camera_yaml_config.items() if value is not None}
"""
    


#######################
# Logging and History #
#######################
import os
from datetime import datetime
from Logger import *


#######################
# Logging and History #
#######################
logging_enabled = config.params["logging"]
runtime_history_dir = config.params["runtime_history_dir"]
if config.params["runtime_folder_override"]:
    runtime_dir = os.path.join(config.params["runtime_folder_override"])
    if os.path.exists(config.params["runtime_folder_override"]):
        shutil.rmtree(config.params["runtime_folder_override"])
else:
    runtime_dir = os.path.join(runtime_history_dir, f"{datetime.now().strftime('%m_%d%-%H_%M_%S')}_flight_testing")

log_files_dir = os.path.join(runtime_dir, "logs")
runtime_log_path = os.path.join(log_files_dir, "runtime.log")
annotation_log_path = os.path.join(log_files_dir, "annotated_images.log")
object_detection_log_path = os.path.join(log_files_dir, "object_detection.log")
georeferencing_log_path = os.path.join(log_files_dir, "georeferencing.log")
optimized_payload_matching_log_path = os.path.join(log_files_dir, "optimized_payload_matching.log")
results_log_path = os.path.join(log_files_dir, "results.log")

os.makedirs(log_files_dir, exist_ok=True)


Custom_Logger.setup_root_logger(runtime_log_path)
annotated_logger = Custom_Logger("annotated", annotation_log_path, logging_enabled)
object_detection_logger = Custom_Logger("object-detection", object_detection_log_path, logging_enabled)
georeferencing_logger = Custom_Logger("georeferencing", georeferencing_log_path, logging_enabled)
optimized_payload_matching_logger = Custom_Logger("optimized-payload-matching", optimized_payload_matching_log_path, logging_enabled)
results_logger = Custom_Logger("results", results_log_path, logging_enabled)


for handler in Custom_Logger.get_root_logger().handlers:
    handler.flush()
    
####################
# Object Detection #
####################
object_detection_model_path = config.params["object_detection"]["model"]
object_detection_model_type = config.params["object_detection"]["model_type"]
object_detection_confidence_threshold = config.params["object_detection"]["confidence_threshold"]
object_detection_device = config.params["object_detection"]["device"]
annotated_detections_dir = os.path.join(runtime_dir, "annotated_detections")
cropped_detections_dir = os.path.join(runtime_dir, "cropped_detections")
source_images_dir = os.path.join(runtime_dir, "source")
contains_unique_targets_dir = os.path.join(runtime_dir, "unique_targets")

detection_model = AutoDetectionModel.from_pretrained(
    model_type = object_detection_model_type,
    model_path = object_detection_model_path,
    confidence_threshold = object_detection_confidence_threshold,
    device = object_detection_device
)

########
# SAHI #
########
sahi_slice = config.params["object_detection"]["sahi"]["slice"]
sahi_slice_height = config.params["object_detection"]["sahi"]["slice_height"]
sahi_slice_width = config.params["object_detection"]["sahi"]["slice_width"]
sahi_overlap_height_ratio = config.params["object_detection"]["sahi"]["overlap_height_ratio"]
sahi_overlap_width_ratio = config.params["object_detection"]["sahi"]["overlap_width_ratio"]
sahi_perform_standard_pred = config.params["object_detection"]["sahi"]["perform_standard_pred"]
sahi_postprocess_match_metric = config.params["object_detection"]["sahi"]["postprocess_match_metric"]
sahi_postprocess_match_threshold = config.params["object_detection"]["sahi"]["postprocess_match_threshold"]


sahi_config = {
    "slice": sahi_slice,
    "slice_height": sahi_slice_height, 
    "slice_width": sahi_slice_width, 
    "overlap_height_ratio": sahi_overlap_height_ratio, 
    "overlap_width_ratio": sahi_overlap_width_ratio, 
    "perform_standard_pred": sahi_perform_standard_pred, 
    "postprocess_match_metric": sahi_postprocess_match_metric, 
    "postprocess_match_threshold": sahi_postprocess_match_threshold
}

sahi_postprocess_config = config.params["object_detection"]["sahi-single-prediction-postprocess"]
sahi_single_prediction_postprocess_options = sahi_postprocess_config["options"]
sahi_single_prediction_postprocess_choice = sahi_postprocess_config["choice"]
sahi_single_prediction_postprocess_match_threshold = sahi_postprocess_config["match_threshold"]
sahi_single_prediction_postprocess_match_metric = sahi_postprocess_config["match_metric"]
sahi_single_prediction_postprocess_class_agnostic = sahi_postprocess_config["class_agnostic"]

sahi_single_prediction_postprocess_config = {
    "postprocess_type": sahi_single_prediction_postprocess_choice,
    "match_threshold": sahi_single_prediction_postprocess_match_threshold,
    "match_metric":sahi_single_prediction_postprocess_match_metric,
    "class_agnostic": sahi_single_prediction_postprocess_class_agnostic
}


##################
# Georeferencing #
##################
altitude_offset = config.params["georeferencing"]['altitude_offset']
sensor_height = config.params["camera"]['sensor_height']
sensor_width = config.params["camera"]['sensor_width']

#############
# Air Drop #
############
bound1 = config.params["airdrop"]["boundary"]["bound_1"]
bound2 = config.params["airdrop"]["boundary"]["bound_2"]
bound3 = config.params["airdrop"]["boundary"]["bound_3"]
bound4 = config.params["airdrop"]["boundary"]["bound_4"]
default_drop_coordinates = calculate_default_drop_coordinates(sort_coordinates([bound1, bound2, bound3, bound4]))

#################
# Initializers #
################
"""DO NOT MODIFY"""
num_photos_processed = 0
last_processed_time = None
timeout = False
timeout_duration = config.params["timeout_duration"]
target_list = []
payload_list = []

#############
# Functions #
#############


def watch_directory():
    global timeout 
    timeout = False
    last_processed_time = time.time()  

    logging.info("File Watcher Initiated")  
    logging.info(f"Watching {watch_dir_path}")

    while num_photos_processed < num_photos and not timeout:
        for file_name in os.listdir(watch_dir_path):
            if num_photos_processed >= num_photos:
                print(f"Reached image limit of {num_photos}")  
                break

            if file_name.endswith((".jpg", ".jpeg", ".png")):
                source_img_path = os.path.join(watch_dir_path, file_name)



                source_img_flag = os.path.splitext(source_img_path)[0]
                source_img_flag_path = f"{source_img_flag}.txt"
                if config.params["debug"] == True:
                    source_img_flag_path = f"{source_img_flag}.txt"
                    while not os.path.exists(source_img_path) or os.path.getsize(source_img_path) == 0 or not os.path.exists(source_img_flag_path):
                        pass

                source_img = Image.open(source_img_path)
                logging.info(f"Processing {source_img_path}")


                source_destination_path = os.path.join(runtime_dir, "source", file_name)
                ODCL(source_img, source_img_path, source_destination_path, detection_model, sahi_config, debug)
                shutil.move(source_img_path, source_destination_path)


                last_processed_time = time.time()


            if time.time() - last_processed_time > timeout_duration:
                timeout = True
                print("Timed out: No new files processed for 30 seconds")
                break  

        if time.time() - last_processed_time > timeout_duration:
            timeout = True
            print(f"Timed out: No new files processed for {timeout_duration} seconds")
            break

        time.sleep(watch_delay)  
    print(f"After loop: {len(target_list)}")
    # Condition below clamps to 4
    if len(target_list) >= len(targets) or num_photos_processed >= num_photos or timeout:
        #m_parameter = config.params[“georeferencing”][“dropzone”]
        #sorted_coords = sort_coordinates(m_parameter)
        #m_coordinates = defaultdropcoordinates(sorted_coords)
        waypoints = Optimized_Payload_Matching(targets, target_list, default_drop_coordinates)
        for i in range(len(waypoints)):
            results_logger.info(f"Target {i}")
            for key, value in waypoints[i].__dict__.items():
                results_logger.info(f"{key}: {value}")
        create_waypoint_file(waypoints, waypoint_file_path)
        create_waypoint_file(waypoints, os.path.join(runtime_dir, waypoint_file_path))
        logging.info(f"Wrote waypoint file for {len(waypoints)} at {waypoint_file_path} and {runtime_dir}/waypoints.txt")

def initialize(runtime_type):
    logging.info("Initializing system...")
    if load_camera_config:
        logging.info("Loading camera configuration")
        load_camera_settings(camera_config_file)
        logging.info("Camera configuration loaded")
    else:
        logging.info("Using existing camera configuration")
    
    os.makedirs(source_images_dir, exist_ok=True)
    logging.info(f"Created source images directory: {source_images_dir}")
    os.makedirs(annotated_detections_dir, exist_ok=True)
    logging.info(f"Created annotated detections directory: {annotated_detections_dir}")
    os.makedirs(cropped_detections_dir, exist_ok=True)
    logging.info(f"Created cropped detections directory: {cropped_detections_dir}")
    logging.info(f"Created annotated detections directory: {contains_unique_targets_dir}")
    os.makedirs(contains_unique_targets_dir, exist_ok=True)
    logging.info("Initialization complete.")


def load_camera_settings(camera_config_file):
    print("Loaded camera settings")
    return 0


def ODCL(img, img_path, source_destination_path, detection_model, sahi_config, debug=False):
    has_unique_targets = 0
    logging.info(f"Running ODCL for {source_destination_path}")
    start_time = time.time()
    results = Object_Detection(img, detection_model, sahi_config, sahi_single_prediction_postprocess_config)
    results.export_visuals(file_name=os.path.splitext(os.path.split(img_path)[1])[0], export_dir=annotated_detections_dir)
    annotated_logger.info(f"Saved annotated image to {annotated_detections_dir}")

    if results.object_prediction_list:
        metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, focal_length = extractMetadata(img_path)
    
        for i in range(len(results.object_prediction_list)):
            if len(target_list) >= 4:
                logging.warning("More than 4 targets detected")
                #break

            predicted_classes = results.object_prediction_list[i].category
            confidence_scores = results.object_prediction_list[i].score.value
            object_detection_logger.info(f"Detected: {predicted_classes} with scores {confidence_scores}")
        
            BB = results.object_prediction_list[i].bbox.to_voc_bbox()
            center_x = (BB[0] + BB[2]) / 2
            center_y = (BB[1] + BB[3]) / 2
            
            target_latitude, target_longitude = Georeference(
                (center_x, center_y), latitude, longitude, altitude, altitude_offset, yaw, sensor_width, sensor_height, pix_width, pix_height, focal_length
            )

            adjusted_BB = adjust_bbox(BB, 10, img.width, img.height)
            
            if not target_list or all(
                abs(haversine(target.latitude, target.longitude, target_latitude, target_longitude)) > 2
                for target in target_list
            ):
                georeferencing_logger.info(f"{source_destination_path}: Potential target at X: {center_x}, Y: {center_y} is located at Lat: {target_latitude}, {target_longitude}")
                cropped = np.array(img.crop(adjusted_BB))
                cropped = cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR)
                cropped_name = f"{os.path.splitext(os.path.split(img_path)[1])[0]}-{center_x}-{center_y}.{os.path.splitext(os.path.split(img_path)[1])[1]}"
                cropped_path = os.path.join(cropped_detections_dir, cropped_name)
                cv2.imwrite(cropped_path, cropped)
                logging.info(f"Saved cropped target to {cropped_path}")
                target = Target(source_destination_path, predicted_classes, confidence_scores, target_latitude, target_longitude)
                target_list.append(target)
                has_unique_targets += 1
                print(f"During loop: {len(target_list)}")

    end_time = time.time() - start_time
    logging.info(f"Completed ODCL for {source_destination_path}. Elapsed Time: {end_time}")
    if has_unique_targets > 0 :
        for i in range(has_unique_targets):
            results.export_visuals(file_name=f"{os.path.splitext(os.path.split(img_path)[1])[0]}-{i}", export_dir=contains_unique_targets_dir)
            annotated_logger.info(f"Saved annotated image to {contains_unique_targets_dir}")
    return 0

if __name__ == "__main__":
    initialize(mode)
    watch_directory()
    print("Completed")
    with open("completed.txt", "w") as f:
        f.write("")


