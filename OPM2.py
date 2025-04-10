import itertools
from classes import Target

CONF_GOOD = 0.5
CONF_BAD = 0.2
MAX_PAYLOADS = 4


def sort_coordinates(coordinates):
    # Sort by y-coordinate in descending order, then by x-coordinate in ascending order
    sorted_by_y = sorted(coordinates, key=lambda coord: (-coord[1], coord[0]))
    
    # Take the two highest points and the two lowest points
    highest_points = sorted_by_y[:2]  # First two points (highest y-values)
    lowest_points = sorted_by_y[2:]   # Remaining two points (lowest y-values)
    
    # Sort each group by x-coordinate (left to right)
    highest_points_sorted = sorted(highest_points, key=lambda coord: coord[0])
    lowest_points_sorted = sorted(lowest_points, key=lambda coord: coord[0])
    
    # Combine the sorted groups
    result = highest_points_sorted + lowest_points_sorted
    return result

def get_midpoint(coordinates):
    long = [coords[0] for coords in coordinates]
    lat = [coords[1] for coords in coordinates]
    midpoint_long = sum(long) / 4
    midpoint_lat = sum(lat) / 4
    return midpoint_lat, midpoint_long

def get_quadrant_index(midpoint, lat, lon):
    midpoint_lat, midpoint_long = midpoint
    if lat >= midpoint_lat and lon <= midpoint_long:
        return 0  # NW
    elif lat >= midpoint_lat and lon > midpoint_long:
        return 1  # NE
    elif lat < midpoint_lat and lon <= midpoint_long:
        return 2  # SW
    else:
        return 3  # SE



def calculate_default_drop_coordinates(coordinates):
    long = [coords[0] for coords in coordinates]
    lat = [coords[1] for coords in coordinates]
    # Calculate the averages
    midpoint_long = sum(long) / 4
    midpoint_lat = sum(lat) / 4
    print(midpoint_long,midpoint_lat)
    defaultdropcoords = []
    # Calculate the average between the midpoint and each of the four corners
    for i in range(len(coordinates)):
        x = (coordinates[i][0])
        y = (coordinates[i][1])
        xave = (midpoint_long + x) / 2
        yave = (midpoint_lat + y) / 2
        mids = (xave,yave)
        defaultdropcoords.append(mids)
    return defaultdropcoords


def calculate_expected_score(confidences, payloads):
    score = 0
    unique_payloads = sum(1 for p in payloads if p > 0)

    for conf, p in zip(confidences, payloads):
        if p > 0:
            score += 20 * p            # survival
            score += 50 * conf * p     # proximity
    score += 30 * unique_payloads      # unique objects
    return score

def create_waypoint_file(targets, waypoint_file_path):
    count = 0
    f = open(waypoint_file_path, "w")
    for target in targets:
        f.write(f"Latitude of payload {count}: {target.latitude}\n")
        f.write(f"Longitude of payload {count}: {target.longitude}\n")
        f.write(f"Number of payloads to drop: {target.num_payloads}\n")
        count += 1
    f.close()

def Optimized_Payload_Matching(valid_target_names, detected_targets, default_coordinates):
    def is_valid_class(cls): return cls in valid_target_names

    scored_detections = []
    for t in detected_targets:
        class_bonus = 0.25 if is_valid_class(t.predicted_classes) else 0.0
        score = t.confidence_scores + class_bonus
        scored_detections.append((t, score))

    scored_detections.sort(key=lambda x: x[1], reverse=True)
    top_targets = [t for t, _ in scored_detections[:4]]

    # Only add dummy targets if we have fewer than 4 real/selected targets
    if len(top_targets) < 4:

        # Central midpoint for quadrant checks
        midpoint = get_midpoint(default_coordinates)


        # Track quadrants already covered by top targets
        used_quadrants = set()
        for t in top_targets:
            used_quadrants.add(get_quadrant_index(midpoint, t.latitude, t.longitude))

        # Add dummy targets in unoccupied quadrants until there's 4 total
        for i, (lon, lat) in enumerate(default_coordinates):
            if len(top_targets) >= 4:
                break
            if i not in used_quadrants:
                dummy = Target("Dummy", 0.0, latitude=lat, longitude=lon)
                top_targets.append(dummy)

    real_targets = [t for t in top_targets if t.predicted_classes != "Dummy"]
    confidences = [t.confidence_scores for t in top_targets]

    # Case 1
    if len(real_targets) == 1:
        conf = real_targets[0].confidence_scores
        if conf >= CONF_GOOD:
            real_targets[0].num_payloads = 4
            for t in top_targets:
                if t is not real_targets[0]:
                    t.num_payloads = 0
        else:
            p_real = round(conf * 4)
            real_targets[0].num_payloads = p_real
            payload_dummies = 4 - p_real
            dummies = [t for t in top_targets if t.predicted_classes == "Dummy"]
            for i, d in enumerate(dummies):
                d.num_payloads = 1 if payload_dummies > 0 else 0
                payload_dummies -= d.num_payloads
        return top_targets

    # Case 2
    if len(real_targets) == 2:
        confs = [t.confidence_scores for t in real_targets]
        if confs[0] >= CONF_GOOD and confs[1] >= CONF_GOOD:
            real_targets[0].num_payloads = 2
            real_targets[1].num_payloads = 2
        elif confs[0] >= CONF_GOOD:
            real_targets[0].num_payloads = 3
            real_targets[1].num_payloads = 1
        elif confs[1] >= CONF_GOOD:
            real_targets[0].num_payloads = 1
            real_targets[1].num_payloads = 3
        elif confs[0] >= CONF_BAD and confs[1] >= CONF_BAD:
            real_targets[0].num_payloads = 2
            real_targets[1].num_payloads = 2
        else:
            real_targets[0].num_payloads = 1
            real_targets[1].num_payloads = 1
            dummies = [t for t in top_targets if t.predicted_classes == "Dummy"]
            for i, d in enumerate(dummies[:2]):
                d.num_payloads = 1
        return top_targets

    # Case 3
    if len(real_targets) == 3:
        high_conf = [t for t in real_targets if t.confidence_scores >= CONF_GOOD]
        if len(high_conf) == 3:
            real_targets[0].num_payloads = 2
            real_targets[1].num_payloads = 1
            real_targets[2].num_payloads = 1
        elif len(high_conf) == 2:
            high_conf[0].num_payloads = 2
            high_conf[1].num_payloads = 1
            low_conf = [t for t in real_targets if t not in high_conf]
            if low_conf:
                low_conf[0].num_payloads = 1
        elif len(high_conf) == 1:
            high_conf[0].num_payloads = 2
            others = [t for t in real_targets if t != high_conf[0]]
            others[0].num_payloads = 1
            others[1].num_payloads = 0
            dummy = [t for t in top_targets if t.predicted_classes == "Dummy"][0]
            dummy.num_payloads = 1
        else:
            for t in real_targets:
                t.num_payloads = 1
            dummy = [t for t in top_targets if t.predicted_classes == "Dummy"][0]
            dummy.num_payloads = 1
        return top_targets

    # Case 4
    possible_payloads = [dist for dist in itertools.product(range(5), repeat=4) if sum(dist) == MAX_PAYLOADS]
    best_payload = None
    best_score = -1
    for dist in possible_payloads:
        score = calculate_expected_score(confidences, dist)
        if score > best_score:
            best_score = score
            best_payload = dist

    for i in range(4):
        top_targets[i].num_payloads = best_payload[i]

    return top_targets


def print_test_results(title, results):
    print(f"\n=== {title} ===")
    for t in results:
        tag = "[Dummy]" if t.predicted_classes == "Dummy" else "       "
        print(f"{tag} {t.predicted_classes:12} | Conf: {t.confidence_scores:.2f} | Payloads: {t.num_payloads}")


if __name__ == "__main__":
    # Valid classes expected in the mission
    targets = ['bus', 'airplane', 'car', 'umbrella']

    # TEST CASE: 0 detections
    test_0 = []
    result_0 = Optimized_Payload_Matching(targets, test_0)
    print_test_results("Case 0 - No Detections", result_0)

    # TEST CASE: 1 detection, high confidence
    t1 = Target("car", 0.85, 34.0, -118.2)
    test_1_high = [t1]
    result_1_high = Optimized_Payload_Matching(targets, test_1_high)
    print_test_results("Case 1 - One Detection (High Confidence)", result_1_high)

    # TEST CASE: 1 detection, low confidence
    t2 = Target("car", 0.35, 34.0, -118.2)
    test_1_low = [t2]
    result_1_low = Optimized_Payload_Matching(targets, test_1_low)
    print_test_results("Case 1 - One Detection (Low Confidence)", result_1_low)

    # TEST CASE: 2 detections, one high confidence
    t3 = Target("car", 0.75, 34.0, -118.2)
    t4 = Target("bus", 0.25, 40.7, -74.0)
    test_2_mixed = [t3, t4]
    result_2_mixed = Optimized_Payload_Matching(targets, test_2_mixed)
    print_test_results("Case 2 - Two Detections (One High Confidence)", result_2_mixed)

    # TEST CASE: 2 detections, both high confidence
    t5 = Target("car", 0.8, 34.0, -118.2)
    t6 = Target("airplane", 0.78, 37.7, -122.4)
    test_2_high = [t5, t6]
    result_2_high = Optimized_Payload_Matching(targets, test_2_high)
    print_test_results("Case 2 - Two Detections (Both High Confidence)", result_2_high)

    # TEST CASE: 3 detections, mixed confidence
    t7 = Target("umbrella", 0.72, 47.6, -122.3)
    t8 = Target("bus", 0.65, 35.2, -120.5)
    t9 = Target("car", 0.25, 33.9, -117.8)
    test_3_mixed = [t7, t8, t9]
    result_3_mixed = Optimized_Payload_Matching(targets, test_3_mixed)
    print_test_results("Case 3 - Three Detections (Mixed Confidence)", result_3_mixed)

    # TEST CASE: 4 detections, scoring-based fallback
    t10 = Target("bus", 0.6, 35.1, -120.3)
    t11 = Target("car", 0.55, 34.2, -118.5)
    t12 = Target("airplane", 0.65, 36.4, -121.7)
    t13 = Target("umbrella", 0.62, 37.0, -122.1)
    test_4 = [t10, t11, t12, t13]
    result_4 = Optimized_Payload_Matching(targets, test_4)
    print_test_results("Case 4 - Four Detections", result_4)

    # TEST CASE: >4 detections
    t14 = Target("sports_ball", 0.4, 33.5, -117.1)
    t15 = Target("bus", 0.2, 30.1, -115.6)
    test_5 = [t10, t11, t12, t13, t14, t15]
    result_5 = Optimized_Payload_Matching(targets, test_5)
    print_test_results("Case 5 - More Than Four Detections", result_5)