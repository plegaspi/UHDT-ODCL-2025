import math
from pyproj import Transformer
from exiftool import ExifToolHelper

def extractMetadata(fileName,sensor_w, sensor_h):
    import math
    with ExifToolHelper() as et:
        metadata = et.get_metadata(fileName)[0]
        # print(metadata['File:Comment'])

        if 'EXIF:GPSLatitude' in metadata and 'EXIF:GPSLongitude' in metadata:
            latitude = metadata['EXIF:GPSLatitude']
            longitude = -metadata['EXIF:GPSLongitude']  # EXIF default is East, but we are in the West
            altitude = metadata['EXIF:GPSAltitude']
            comment = metadata['File:Comment']
            yaw= float([component.split(":")[1] for component in comment.split() if component.startswith("yaw:")][0])
            pix_width = metadata['File:ImageWidth']
            pix_height = metadata["File:ImageHeight"]
            dpi_resolution = metadata['EXIF:XResolution']
            focal_length = metadata['EXIF:FocalLength']
            #sensor_width = pix_width/dpi_resolution
            #sensor_height = pix_height/dpi_resolution
            horiz_fov =  2*math.degrees(math.atan(sensor_w/focal_length))
            vert_fov = 2*math.degrees(math.atan(sensor_h/focal_length))
            return metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, horiz_fov, vert_fov, 

def georeference(drone_latitude, drone_longitude, drone_altitude, drone_yaw, pix_width, pix_height, horiz_fov, vert_fov,  target_pixel_coordinates):
    # Constants for image resolution and camera field of view
    pixel_resolution = (pix_width,pix_height) # Image pixel dimensions
    horizontal_fov = horiz_fov  # Horizontal field of view in degrees
    vertical_fov = vert_fov   # Vertical field of view in degrees

    # Calculate the real-world dimensions of the image at the target altitude
    image_width = 2 * drone_altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * drone_altitude * math.tan(math.radians(vertical_fov / 2))

    # Calculate the UTM zone based on the drone's initial longitude
    utm_zone = int((drone_longitude + 180) // 6) + 1
    hemisphere_code = 326 if drone_latitude >= 0 else 327  # 326 for Northern Hemisphere, 327 for Southern
    crs_projected = f"EPSG:{hemisphere_code}{utm_zone:02d}"  # Complete EPSG code for UTM zone

    # Initialize pyproj transformers for coordinate conversions
    transformer = Transformer.from_crs("EPSG:4326", crs_projected, always_xy=True)
    inv_transformer = Transformer.from_crs(crs_projected, "EPSG:4326", always_xy=True)

    # Convert the drone's initial GPS coordinates to UTM
    drone_x, drone_y = transformer.transform(drone_longitude, drone_latitude)

    # Target pixel offset from image center
    target_pixel_x, target_pixel_y = target_pixel_coordinates
    image_center_x, image_center_y = pixel_resolution[0] / 2, pixel_resolution[1] / 2
    delta_x, delta_y = target_pixel_x - image_center_x, target_pixel_y - image_center_y

    # Adjust for drone's yaw (orientation)
    drone_yaw_rad = math.radians(drone_yaw)
    corrected_delta_x = delta_x * math.cos(drone_yaw_rad) - delta_y * math.sin(drone_yaw_rad)
    corrected_delta_y = delta_x * math.sin(drone_yaw_rad) + delta_y * math.cos(drone_yaw_rad)

    # Convert pixel offsets to meters
    x_meters = corrected_delta_x * image_width / pixel_resolution[0]
    y_meters = corrected_delta_y * image_height / pixel_resolution[1]

    # Calculate the target position in UTM coordinates by adding the offsets
    target_x = drone_x + x_meters
    target_y = drone_y + y_meters

    # Convert the final target position back to GPS coordinates
    target_longitude, target_latitude = inv_transformer.transform(target_x, target_y)

    return target_latitude, target_longitude 

#Return Distance Between Two GPS points in meters
def haversine(lat1, lon1, lat2, lon2):

    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    radius = 6371 # Radius of earth in kilometers. Use 3956 for miles
    distance = radius * c * 1000 # Convert to meters

    return distance

if __name__ == '__main__':
    target_pixel_coordinates = (428,2133)
    image_file = r"C:\\Users\\dillo\\image10.jpg"
    sensor_width = 23.55
    sensor_height = 15.6
    actual_lat = 21.400354
    actual_long = -157.764322
    metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, horiz_fov, vert_fov = extractMetadata(image_file,sensor_width, sensor_height )
    target_latitude, target_longitude = georeference(latitude, longitude, altitude, yaw, pix_width, pix_height, horiz_fov, vert_fov, target_pixel_coordinates)
    distance = haversine(target_latitude, target_longitude,actual_lat, actual_long)
    print(f'GPS Latitude:{target_latitude} GPS Longitude:{target_longitude}')
    print(f'Distance from Actual Coordinates: {distance}')
  


#lat, long = georeference(21.4003061000022, -157.764225299983, 24.913, 1.2410184144973755, 6000 ,4000 ,59.745278500871386, 41.66241920241201, (428,2133))

