# Only need to change inputDirectory to the folder where your labels are

import os

cwd = os.getcwd()

# Change this to the directory with your labels
inputDirectory = r"C:\Users\dynam\OneDrive\Desktop\Test\bus.v1i.yolov9\valid\labels"

outputDirectoryName = r"Converted_Labels"
# Directory where converted labels will be saved
outputFilePath = os.path.join(cwd, "Converted_Labels")
os.mkdir(outputDirectoryName)
count = 0
for name in os.listdir(inputDirectory):
    with open(os.path.join(inputDirectory, name)) as inputfile:
        print(name)

        for line in inputfile:
            currentLine = line.strip()
            lineSplit = currentLine.split()
            for i in range(0,len(lineSplit)):
                lineSplit[i] = float(lineSplit[i])
            class_id = int(lineSplit[0])
            min_x = lineSplit[1]
            min_y = lineSplit[2]
            max_x = lineSplit[1]
            max_y = lineSplit[2]
            for i in range(1, len(lineSplit)):
                if i%2 == 1:
                    if lineSplit[i] > max_x:
                        max_x = lineSplit[i]
                    if lineSplit[i] < min_x:
                        min_x = lineSplit[i]
                if i%2 == 0:
                    if lineSplit[i] > max_y:
                        max_y = lineSplit[i]
                    if lineSplit[i] < min_y:
                        min_y = lineSplit[i]
            center_x = (max_x+min_x)/2
            center_y = (max_y+min_y)/2
            height = max_y-min_y
            width = max_x-min_x
            print(f"{class_id} {center_x} {center_y} {width} {height}\n")

            if count == 0:
                with open(os.path.join(outputFilePath,name), 'w') as outputfile:
                    outputfile.write(f"{class_id} {center_x} {center_y} {width} {height}\n")
            else:
                with open(os.path.join(outputFilePath,name), 'a') as outputfile:
                    outputfile.write(f"{class_id} {center_x} {center_y} {width} {height}\n")
            count = count+1
        
    print()