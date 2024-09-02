servo_port = [0,1,2,3]
alt = 24.38 #meters
target_format = ["A", "B", "C", "D"]
servo_PWM = 1100

def deliveryScript(PayloadList, TargetList):
    count = 0
    f = open("/home/uhdt/UAV_software/Autonomous/Official/FINAL CODE/payload_coord.txt", "w")
    #f = open("payload_coord.txt", "w")
    for target in TargetList:
        f.write(F"Latitude of payload {target_format[count]}: {target.latitude}\n")
        f.write(F"Longitude of payload {target_format[count]}: {target.longitude}\n")
        f.write(F"Compartment of payload {target_format[count]}: {PayloadList[count].dock}\n")
        f.write(F"\n")
        count += 1
    f.close()