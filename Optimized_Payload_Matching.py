from classes import Target
import os

def Optimized_Payload_Matching(targets, target_list):
    # Should return an array of Targets with properties of latitude, longitude, and number of payloads to be dropped
    # Use the Target object class
    # Validate that the number of payloads to be dropped across all four targets is no greater than the number of targets set in Config
    matched_payloads = []
    for target in target_list:
        target.num_payloads = 1
        matched_payloads.append(target)
    return matched_payloads

def create_waypoint_file(targets, waypoint_file_path):
    count = 0
    f = open(waypoint_file_path, "w")
    for target in targets:
        f.write(f"Latitude of payload {count}: {target.latitude}\n")
        f.write(f"Longitude of payload {count}: {target.longitude}\n")
        f.write(f"Number of payloads to drop: {target.num_payloads}\n")
        count += 1
    f.close()

def compare(payload, target):
    return 0

def match_payloads(payloads, targets):
    return 0
  