import os
import mpe_functions as mpe
object_classes = ["person", "motorcycle", "car", "airplane", "bus", "boat", "stop_sign", "snowboard", "umbrella", "sports_ball", "baseball_bat", "bed", "tennis_racket", "suitcase"]

directory = "labels_MPE_script_testing"

# Iterate over files in directory
for file in os.listdir(directory):
    # Open file
    with open(os.path.join(directory, file)) as f:
        #print(f"Content of '{f.name}'")
        # Read content of file
        #print(f.read())
        print(f'the # of {object_classes[0]} for {f.name} is {mpe.get_NoD_class(f.name,0)}')
