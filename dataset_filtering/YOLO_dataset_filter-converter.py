import os

#CHANGE THIS TO FOLDER CONTAINING THE IMAGE ANNOTATIONS
folder_path = os.path.join("COCO Dataset.v34 test labels")

#CHANGE THIS FOR DESIRED OBJECT
object_of_interest = "person"
#different datasets have different numbers for each classified object, this function finds it in the data files.
def get_object_classnum(data_file_name):
    object_class_line = ""
    object_class_num = 0
    for line in open(f'{data_file_name}'):
        if "names:" in line:
            object_class_line = line
            break
    object_class_list_scuffed = object_class_line[8:len(object_class_line)-2].split(",")
    #print(object_class_list_scuffed[62]) #should print "Stop sign"
    for thing in object_class_list_scuffed:
        if object_of_interest in thing:
            object_class_num = object_class_list_scuffed.index(thing)
            break

    return object_class_num


def filter_list(file_name, object_class_num):
    bufferlist = [line for line in open(f'{file_name}') if object_class_num == int(line[0:2])]
    #print(bufferlist, len(bufferlist))
    namebuffer = file_name.split("\\")[1][0:12]
    #print(namebuffer)
    open(f'{namebuffer}_filtered_list','w').writelines(bufferlist)
    #open(f'filtered_list','a').writelines(bufferlist)
    #print(f'{object_class_num} ye')
    '''
    with open(f'{folder_path}_annotations_filtered.txt', 'w') as fx:
        for line in open(f'{file_name}'):
            if(object_class_num == int(line[0:2])):
                fx.write(f'{line}\n')
                print(f'{object_class_num} = {line[0:2]}\n')
                '''
 
object_class_num = get_object_classnum("data.yaml")
#print(type(folder_path))
for file in os.listdir(folder_path):
    #print(os.path.join(folder_path, file))
    #print(file)
    filter_list(os.path.join(folder_path, file), object_class_num)

#This should create a "xx_filtered" file for each file in the folder path specified (xx being the file name).

#TODO!!! Need to set a folder to put theses outputs to
