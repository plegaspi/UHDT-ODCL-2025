import os
import time
import shutil
import numpy as np
import cv2
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from PIL import Image
from georef import georeference, haversine
from metadataExtractor2 import extractMetadata
from classes import Target, Payload
from payloadDelivery import deliveryScript
from objectdetect import adjust_bbox
from color import color_classification
from shape import shape_classification
from alphanum import image2textRotate
from Close_Enough_Test_Cases import compare, order_payloads
import math

"""
##valid_shapes: ["CIRCLE", "CROSS", "PENTAGON", "QUARTERCIRCLE", "RECTANGLE", "SEMICIRCLE", "STAR", "TRIANGLE" ]
##valid_colors: ["RED", "ORANGE", "YELLOW", "BLUE", "GREEN", "PURPLE", "BROWN", "BLACK", "WHITE"]
"""

#Payload 1 Info
dock1 = 0
shape1 = "QUARTERCIRCLE"
shapeColor1 = "BLUE" 
alphanumColor1 = "BLACK"
alphanum1 = "E"

#Payload 2 Info
dock2 = 1
shape2 = "RECTANGLE"
shapeColor2 = "RED" 
alphanumColor2 = "BLACK"
alphanum2 = "K"

#Payload 3 Info
dock3 = 3
shape3 = "STAR"
shapeColor3 = "BROWN" 
alphanumColor3 = "BLACK"
alphanum3 = "I"

#Payload 4 Info
dock4 = 2
shape4 = "TRIANGLE"
shapeColor4 = "ORANGE" 
alphanumColor4 = "WHITE"
alphanum4 = "3"

target_shapes = [shape1, shape2, shape3, shape4]
target_shape_colors = [shapeColor1, shapeColor2, shapeColor3, shapeColor4]
target_alphanum_colors = [alphanumColor1, alphanumColor2, alphanumColor3, alphanumColor4]
target_alphanum = [alphanum1, alphanum2, alphanum3,alphanum4]

targetList = []
payloadList = []
alphanum_whitelist = f"{alphanum1}{alphanum2}{alphanum3}{alphanum4}"
trash = 'old'

def spell_check(target_shapes, target_shape_colors, target_alphanum_colors, target_alphanum):
    valid_shapes = ["CIRCLE", "CROSS", "PENTAGON", "QUARTERCIRCLE", "RECTANGLE", "SEMICIRCLE", "STAR", "TRIANGLE" ]
    valid_colors = ["RED", "ORANGE", "YELLOW", "BLUE", "GREEN", "PURPLE", "BROWN", "BLACK", "WHITE"]

    for i in range(4):
        if target_shapes[i].upper() not in valid_shapes:
            print(f"Invalid shape for target {i+1}")
            exit(1)
        if target_shape_colors[i].upper() not in valid_colors:
            print(f"Invalid color for target {i+1}")
            exit(1)
        if target_alphanum_colors[i].upper() not in valid_colors:
            print(f"Invalid color for target {i+1}")
            exit(1)
        if len(target_alphanum[i]) != 1 or not target_alphanum[i].isalnum():
            print(f"Invalid alphanumeric for target {i+1}")
            exit(1)

spell_check(target_shapes, target_shape_colors, target_alphanum_colors, target_alphanum)

detection_model = AutoDetectionModel.from_pretrained(
    model_type='yolov8',
    model_path='weight/nanotarget1.pt',
    confidence_threshold=0.5,
    device='cuda:0'
)

def watch_directory():
    print("File Watcher Initiated")
    processed_count = 0
    pic_count = 28
    path = "/home/uhdt/UAV_software/Autonomous/watchdog"
    #path = "watchdog"
    last_processed_time = None
    time_out = False

    while (len(targetList) < 4) and (processed_count < pic_count) and not time_out:
        for filename in os.listdir(path):
            if (processed_count > pic_count):
                print("Image limit!")
                break;
            if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                full_path = os.path.join(path, filename)
                
                # Wait until the file is fully created
                while True:
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                        break
                    time.sleep(1)

                # Process the image file
                ODCL(full_path)
                # Move the image file
                shutil.move(full_path, f'{trash}/{filename}')
                processed_count += 1
                last_processed_time = time.time()  # Update the last processed time
                print(f"Processed: {processed_count}/{pic_count}")
        
        # Check if more than __ seconds have passed since the last image was processed
        if last_processed_time and (time.time() - last_processed_time) > 30:
            time_out = True  # Set the time_out flag to True
            print("Time out!")
            break;
                
        time.sleep(2) # Check directory every __ seconds
    
    if(len(targetList) >= 4) or (processed_count >=pic_count) or time_out:
        ordered_payloads = order_payloads(payloadList, targetList)
        deliveryScript(ordered_payloads, targetList)
        print("Done")

def ODCL(path):
    print(f"{path}")
    image = Image.open(f'{path}')
    result = get_sliced_prediction(
        image,
        detection_model,
        slice_height=640,
        slice_width=640,
        overlap_height_ratio=0.11,
        overlap_width_ratio=0.11,
        perform_standard_pred=False,
        postprocess_match_metric='IOU',
        postprocess_match_threshold=0.3
    )
    
    if (result.object_prediction_list != None):
        metadata, latitude, longitude, altitude, yaw = extractMetadata(f"{path}")


        for i in range(len(result.object_prediction_list)):
            if (len(targetList) >= 4):
                print("Target Limit Reached")
                break;
            BB = result.object_prediction_list[i].bbox.to_voc_bbox()
            
            center_x = (BB[0] + BB[2]) / 2
            center_y = (BB[1] + BB[3]) / 2
            target_latitude, target_longitude = georeference(latitude, longitude, altitude, yaw, (center_x, center_y))

            adjusted_BB = adjust_bbox(BB, 10, image.width, image.height)

            #Check if duplicate Target
            if not targetList or all(abs(haversine(target.latitude, target.longitude, target_latitude, target_longitude)) > 3 for target in targetList):
                cropped = np.array(image.crop(adjusted_BB))
                cropped = cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR)
                shape = shape_classification(cropped)

                print(f"Shape: {shape}")
                shape_color, alphanum_color, shape_HSV, alphanum_HSV, shape_mask, alphanum_mask, k_means_mask = color_classification(cropped)                

                print(f"Shape Color:{shape_color}  Alphanum Color:{alphanum_color}")
                
            

                shape_mask = cv2.cvtColor(shape_mask, cv2.COLOR_GRAY2RGB)
                alphanum_mask = cv2.cvtColor(alphanum_mask, cv2.COLOR_GRAY2RGB)
                alphanum1, alphanum1_conf = image2textRotate(alphanum_mask, alphanum_whitelist)


                if alphanum1_conf < 0.5:
                    alphanum2, alphanum2_conf = image2textRotate(shape_mask, alphanum_whitelist)
                    if alphanum2_conf > alphanum1_conf:
                        alphanum1 = alphanum2
                        alphanum1_conf = alphanum2_conf
                
                print(f"Alphanum: {alphanum1}")

                target = Target(shape.upper(), target_latitude, target_longitude, shape_color.upper(), alphanum_color.upper(), alphanum1.upper())
                targetList.append(target)



payload1 = Payload(dock1, shape1.upper(), shapeColor1.upper(), alphanumColor1.upper(), alphanum1.upper()); payloadList.append(payload1); print("Payload 1 Added")
payload2 = Payload(dock2, shape2.upper(), shapeColor2.upper(), alphanumColor2.upper(), alphanum2.upper()); payloadList.append(payload2); print("Payload 2 Added")
payload3 = Payload(dock3, shape3.upper(), shapeColor3.upper(), alphanumColor3.upper(), alphanum3.upper()); payloadList.append(payload3); print("Payload 3 Added")
payload4 = Payload(dock4, shape4.upper(), shapeColor4.upper(), alphanumColor4.upper(), alphanum4.upper()); payloadList.append(payload4); print("Payload 4 Added")
watch_directory()