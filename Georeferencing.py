import math
from pyproj import Transformer
import math
import pymap3d as pm
from exiftool import ExifToolHelper

def extractMetadata(fileName):
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
            return metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, focal_length

def Georeference(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length):
    # Constants for image resolution and camera field of view
    pixel_resolution = (pix_width, pix_height) # Image pixel dimensions
    horizontal_fov =  2*math.degrees(math.atan(sensor_w/(2*focal_length)))
    vertical_fov = 2*math.degrees(math.atan(sensor_h/(2*focal_length)))

    altitude = drone_altitude - altitude_offset
    
    # Calculate the real-world dimensions of the image at the target altitude
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))

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
    delta_y *= 1

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
  

def Georeference1(
    target_pixel_coordinates,
    drone_latitude, drone_longitude, drone_altitude,
    altitude_offset, drone_yaw,
    sensor_w, sensor_h, pix_width, pix_height, focal_length
):
    # Adjust altitude if necessary
    altitude = drone_altitude - altitude_offset

    # Field of view
    horizontal_fov = 2 * math.degrees(math.atan(sensor_w / (2 * focal_length)))
    vertical_fov = 2 * math.degrees(math.atan(sensor_h / (2 * focal_length)))

    # Ground footprint dimensions at altitude
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))

    # Image center and pixel offset
    image_center_x, image_center_y = pix_width / 2, pix_height / 2
    target_pixel_x, target_pixel_y = target_pixel_coordinates

    delta_x = target_pixel_x - image_center_x
    delta_y = target_pixel_y - image_center_y
    delta_y *= 1  # Flip y to match ENU

    # Rotate according to yaw (convert to radians)
    yaw_rad = math.radians(drone_yaw)
    corrected_dx = delta_x * math.cos(yaw_rad) - delta_y * math.sin(yaw_rad)
    corrected_dy = delta_x * math.sin(yaw_rad) + delta_y * math.cos(yaw_rad)

    # Convert from pixel offset to real-world distance in meters
    east_offset = corrected_dx * image_width / pix_width
    north_offset = corrected_dy * image_height / pix_height
    up_offset = 0  # Nadir view, so no change in vertical

    # Convert local ENU offset back to GPS
    target_lat, target_lon, _ = pm.enu2geodetic(
        east_offset, north_offset, up_offset,
        drone_latitude, drone_longitude, drone_altitude
    )

    return target_lat, target_lon
  
def Georeference2(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length):
    # Constants for image resolution and camera field of view
    pixel_resolution = (pix_width, pix_height)  # Image pixel dimensions
    horiz_fov =  2*math.degrees(math.atan(sensor_w/(2*focal_length)))
    vert_fov = 2*math.degrees(math.atan(sensor_h/(2*focal_length)))
    horizontal_fov = horiz_fov  # Horizontal field of view in degrees
    vertical_fov = vert_fov     # Vertical field of view in degrees

    altitude = drone_altitude - altitude_offset

    # Calculate the real-world dimensions of the image at the target altitude
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))

    # --- Custom Projection Block ---
    # Define an Azimuthal Equidistant projection centered on the drone coordinates.
    proj_string = f"+proj=aeqd +lat_0={drone_latitude} +lon_0={drone_longitude} +ellps=WGS84 +units=m +no_defs"
    transformer = Transformer.from_crs("EPSG:4326", proj_string, always_xy=True)
    inv_transformer = Transformer.from_crs(proj_string, "EPSG:4326", always_xy=True)
    # Convert the drone's GPS coordinates to the custom projection coordinates.
    drone_x, drone_y = transformer.transform(drone_longitude, drone_latitude)
    # --- End Custom Projection Block ---

    # Target pixel offset from image center
    target_pixel_x, target_pixel_y = target_pixel_coordinates
    image_center_x, image_center_y = pixel_resolution[0] / 2, pixel_resolution[1] / 2
    delta_x, delta_y = target_pixel_x - image_center_x, target_pixel_y - image_center_y
    delta_y *= 1

    # Adjust for drone's yaw (orientation)
    drone_yaw_rad = math.radians(drone_yaw)
    corrected_delta_x = delta_x * math.cos(drone_yaw_rad) - delta_y * math.sin(drone_yaw_rad)
    corrected_delta_y = delta_x * math.sin(drone_yaw_rad) + delta_y * math.cos(drone_yaw_rad)

    # Convert pixel offsets to meters
    x_meters = corrected_delta_x * image_width / pixel_resolution[0]
    y_meters = corrected_delta_y * image_height / pixel_resolution[1]

    # Calculate the target position in custom projection coordinates by adding the offsets
    target_x = drone_x + x_meters
    target_y = drone_y + y_meters

    # Convert the final target position back to GPS coordinates
    target_longitude, target_latitude = inv_transformer.transform(target_x, target_y)

    return target_latitude, target_longitude

def Georeference3(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length):
    # Constants
    pixel_resolution = (pix_width, pix_height)
    
    # Camera field of view = 2*arctan(sensor_size/(2*focal_length))
    horizontal_fov = 2*math.degrees(math.atan(sensor_w/(2*focal_length))) # degrees
    vertical_fov =  2*math.degrees(math.atan(sensor_h/(2*focal_length))) # degrees 

    altitude = drone_altitude - altitude_offset


    # Image real-world dimensions
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))
    
    # Drone orientation
    drone_yaw_rad = math.radians(drone_yaw)

    # Target pixel coordinates
    target_pixel_x, target_pixel_y = target_pixel_coordinates

    # Image center coordinates
    image_center_x = pixel_resolution[0] / 2
    image_center_y = pixel_resolution[1] / 2

    # Calculate distance from image center to target pixel
    delta_x = target_pixel_x - image_center_x
    delta_y = target_pixel_y - image_center_y
    delta_y *= 1

    # Calculate distance from image center to target pixel after correction
    corrected_delta_x = delta_x * math.cos(drone_yaw_rad) - delta_y * math.sin(drone_yaw_rad)
    corrected_delta_y = delta_x * math.sin(drone_yaw_rad) + delta_y * math.cos(drone_yaw_rad)

    # Calculate new target pixel coordinates after adjustment
    corrected_target_pixel_x = image_center_x + corrected_delta_x
    corrected_target_pixel_y = image_center_y + corrected_delta_y

    # Calculate target coordinates in meters (assuming linear relationship)
    x_meters = (corrected_target_pixel_x - image_center_x) * image_width / pixel_resolution[0]
    y_meters = (corrected_target_pixel_y - image_center_y) * image_height / pixel_resolution[1]

    # Convert drone-centric coordinates to global coordinates
    target_latitude = drone_latitude + (y_meters / 111319.944)
    target_longitude = drone_longitude + (x_meters / (111319.944 * math.cos(math.radians(drone_latitude))))

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
    target_pixel_coordinates = (1079.4033203125, 3303.25146484375)
    image_file = "/Users/plegaspi/Documents/UHDT/UHDT-ODCL-2025/runtime/20250414_234100_flight_testing/source/11.jpg"
    sensor_width = 23.55
    sensor_height = 15.6
    actual_coords = (21.4002798, -157.7644341)
    actual_lat, actual_long = actual_coords
    altitude_offset = 0
    mmetadata, latitude, longitude, altitude, yaw, pix_width, pix_height, focal_length = extractMetadata(image_file)
    target_latitude, target_longitude = Georeference(target_pixel_coordinates, latitude, longitude, altitude, altitude_offset, yaw, sensor_width, sensor_width, pix_width, pix_height, focal_length)
    target_latitude1, target_longitude1 = Georeference1(target_pixel_coordinates, latitude, longitude, altitude, altitude_offset, yaw, sensor_width, sensor_width, pix_width, pix_height, focal_length)
    target_latitude2, target_longitude2 = Georeference2(target_pixel_coordinates, latitude, longitude, altitude, altitude_offset, yaw, sensor_width, sensor_width, pix_width, pix_height, focal_length)
    target_latitude3, target_longitude3 = Georeference3(target_pixel_coordinates, latitude, longitude, altitude, altitude_offset, yaw, sensor_width, sensor_width, pix_width, pix_height, focal_length)
    distance = haversine(target_latitude, target_longitude,actual_lat, actual_long)
    distance1 = haversine(target_latitude1, target_longitude1,actual_lat, actual_long)
    distance2 = haversine(target_latitude2, target_longitude2,actual_lat, actual_long)
    distance3 = haversine(target_latitude3, target_longitude3,actual_lat, actual_long)
    print(f'GPS Latitude:{target_latitude} GPS Longitude:{target_longitude}')
    print(f'GPS Latitude:{target_latitude1} GPS Longitude:{target_longitude}')
    print(f'GPS Latitude:{target_latitude2} GPS Longitude:{target_longitude2}')
    print(f'GPS Latitude:{target_latitude3} GPS Longitude:{target_longitude3}')
    print(f'Distance from Actual Coordinates: {distance}')
    print(f'Distance from Actual Coordinates: {distance1}')
    print(f'Distance from Actual Coordinates: {distance2}')
    print(f'Distance from Actual Coordinates: {distance3}')
  


#lat, long = georeference(21.4003061000022, -157.764225299983, 24.913, 1.2410184144973755, 6000 ,4000 ,59.745278500871386, 41.66241920241201, (428,2133))

