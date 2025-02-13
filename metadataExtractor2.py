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
        
metadata, latitude, longitude, altitude, yaw, width, height, horiz_fov, vert_fov, = extractMetadata(r"C:\\Users\\dillo\\image10.jpg",23.55,15.6)

#print(latitude, longitude, altitude, yaw, width, height, horiz_fov, vert_fov)
