##########
# Utils #
#########
from metadataExtractor2 import extractMetadata
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
import colorlog


##########
# Config #
##########
from Config import Config
from classes import Target


###################
# ODCL Algorithms #
###################
from Object_Detection import Object_Detection, adjust_bbox
from Georeferencing import Georeference, haversine
from Optimized_Payload_Matching import Optimized_Payload_Matching, create_waypoint_file


#####################
# Payload Delivery  #
#####################
from payloadDelivery import deliveryScript


#################
# Configuration #
#################
config = Config("config/config.yaml")
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
load_camera_config = config.params["camera"]["load_config"]
camera_config_file = config.params["camera"]["config"]


#######################
# Logging and History #
#######################
import logging
import colorlog
import os
from datetime import datetime


#######################
# Logging and History #
#######################
runtime_history_dir = config.params["runtime_history_dir"]
if config.params["runtime_folder_override"] != "":
    runtime_dir = os.path.join(config.params["runtime_folder_override"])
    if os.path.exists(config.params["runtime_folder_override"]):
        shutil.rmtree(config.params["runtime_folder_override"])
else:
    runtime_dir = os.path.join(runtime_history_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_flight_testing")
log_files_dir = os.path.join(runtime_dir, "logs")

runtime_log_path = os.path.join(log_files_dir, "runtime.log")
annotation_log_path = os.path.join(log_files_dir, "annotated_images.log")
object_detection_log_path = os.path.join(log_files_dir, "object_detection.log")
georeferencing_log_path = os.path.join(log_files_dir, "georeferencing.log")
optimized_payload_matching_log_path = os.path.join(log_files_dir, "optimized_payload_matching.log")
results_log_path = os.path.join(log_files_dir, "results.log")

os.makedirs(log_files_dir, exist_ok=True)

COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[34m"
COLOR_CYAN = "\033[36m"
COLOR_MAGENTA = "\033[35m"
COLOR_WHITE = "\033[37m"


LOGGER_COLORS = {
    "annotated": COLOR_BLUE,
    "object-detection": COLOR_CYAN,
    "georeferencing": COLOR_MAGENTA,
    "optimized-payload-matching": COLOR_WHITE,
}


LOG_LEVEL_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

logging.getLogger("matplotlib").setLevel(logging.WARNING)


class CustomColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        log_color = LOGGER_COLORS.get(record.name, COLOR_RESET) 
        timestamp = f"{log_color}{self.formatTime(record)}{COLOR_RESET}"  
        record.asctime = timestamp 
        return super().format(record) 
def create_logger(name, log_file):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)


    logger.propagate = True  


    if not logger.handlers:
        formatter = CustomColoredFormatter(
            log_format,
            log_colors=LOG_LEVEL_COLORS,
            reset=True,
            style="%",
        )


        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)


        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


log_format = "%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(message)s"


root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)


if not any(isinstance(h, logging.FileHandler) and h.baseFilename == runtime_log_path for h in root_logger.handlers):
    runtime_handler = logging.FileHandler(runtime_log_path)
    runtime_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    root_logger.addHandler(runtime_handler)  


if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
    root_logger.addHandler(logging.StreamHandler())



annotated_logger = create_logger("annotated", annotation_log_path)
object_detection_logger = create_logger("object-detection", object_detection_log_path)
georeferencing_logger = create_logger("georeferencing", georeferencing_log_path)
optimized_payload_matching_logger = create_logger("optimized-payload-matching", optimized_payload_matching_log_path)
results_logger = create_logger("results", results_log_path)


for handler in root_logger.handlers:
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

#################
# Initializers #
################
"""DO NOT MODIFY"""
num_photos_processed = 0
last_processed_time = None
timeout = False
target_list = []
payload_list = []

#############
# Functions #
#############


def watch_directory():
    global timeout 
    timeout = False
    last_processed_time = time.time()  
    timeout_duration = 30  

    logging.info("File Watcher Initiated")  
    logging.info(f"Watching {watch_dir_path}")

    while len(target_list) < len(targets) and num_photos_processed < num_photos and not timeout:
        for file_name in os.listdir(watch_dir_path):
            if num_photos_processed >= num_photos:
                print(f"Reached image limit of {num_photos}")  
                break

            if file_name.endswith((".jpg", ".jpeg", ".png")):
                source_img_path = os.path.join(watch_dir_path, file_name)


                while not os.path.exists(source_img_path) or os.path.getsize(source_img_path) == 0:
                    time.sleep(1)

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
            print("Timed out: No new files processed for 30 seconds")
            break

        time.sleep(watch_delay)  
    print(f"After loop: {len(target_list)}")
    if len(target_list) >= len(targets) or num_photos_processed >= num_photos or timeout:
        waypoints = Optimized_Payload_Matching(targets, target_list)
        create_waypoint_file(target_list, waypoint_file_path)
        create_waypoint_file(target_list, runtime_dir)
        logging.info(f"Wrote waypoint file for {len(target_list)} at {waypoint_file_path} and {runtime_dir}/waypoints.txt")

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
    results = Object_Detection(img, detection_model, sahi_config)
    if debug:
        results.export_visuals(file_name=os.path.splitext(os.path.split(img_path)[1])[0], export_dir=annotated_detections_dir)
        annotated_logger.info(f"Saved annotated image to {annotated_detections_dir}")

    if results.object_prediction_list:
        metadata, drone_latitude, drone_longitude, drone_altitude, drone_yaw = extractMetadata(img_path)
    
    
    for i in range(len(results.object_prediction_list)):
        if len(target_list) >= 4:
            logging.warning("Target Limit Reached")
            break

        predicted_classes = results.object_prediction_list[i].category
        confidence_scores = results.object_prediction_list[i].score
        object_detection_logger.info(f"Detected: {predicted_classes} with scores {confidence_scores}")
    
        BB = results.object_prediction_list[i].bbox.to_voc_bbox()
        center_x = (BB[0] + BB[2]) / 2
        center_y = (BB[1] + BB[3]) / 2
        
        target_latitude, target_longitude = Georeference(
            drone_latitude, drone_longitude, drone_altitude, drone_yaw, (center_x, center_y)
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
            target = Target(predicted_classes, confidence_scores, target_latitude, target_longitude)
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