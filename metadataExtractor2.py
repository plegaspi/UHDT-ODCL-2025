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
            return metadata, latitude, longitude, altitude, yaw
        
#metadata, latitude, longitude, altitude, yaw = extractMetadata("/home/uhdt/UAV_software/Autonomous/watchdog/image1_27.jpg")

#print(yaw)