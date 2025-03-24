import csv
import os


#print(os.getcwd())

#/Users/Chris/Documents/Missclassifications - Sheet1.csv
"""
def update_missclaification (file_name, column_name, old_value, new_value):
    with open(file_name, 'r') as file:
        reader= csv.DictReader(file)
        data = list(reader)

    for row in data:
        
    with open (file_name, 'w', newline=' '):
"""

#getting the misclassifications per class function
def per_class_misclassification (column_name, old_value, new_value):
     return



#def get_misclassification():

def get_missclassifications(file_name):
    with open(file_name, 'r') as file:
        reader= list(csv.DictReader(file))
        print(reader[0])
        
       
        header_row= list(reader[0].values())
        misclassification_row_index = None

        for i in range(len(reader)):
              row_name = reader[i]["Class"]
              if row_name == "Misclassifications":
                    misclassification_row_index = i
        missclassification_row = list(reader[misclassification_row_index].values())
        
        column_position_index = 1
        end_column_index = len(missclassification_row)

        while column_position_index < end_column_index:
            print(header_row[column_position_index]) 
            print(missclassification_row[column_position_index])
            column_position_index +=1
            
   

if __name__ == "__main__":
     get_missclassifications("original.csv")