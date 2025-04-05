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



# Function to get misclassifications and correct classifications (diagonal/correct values)
def get_misclassifications(file_name):
    with open(file_name, 'r') as file:
        reader = list(csv.DictReader(file))
        

        # Extract headers (class names/the first row)
        header_row = list(reader[0].keys())

        # Skip the first column ("class")
        class_names = header_row[1:]
        
        # a list to store diagonal values (correct classifications)
        diagonal = []
       
        # a dictionary to store misclassifications
        misclassifications = {}

        # Go through each row to extract diagonal and misclassifications
        for row in reader:
            
            # Get the class name for the row
            row_class = row["class"].strip() 
            misclassifications[row_class] = []

            for col_index, col_class in enumerate(class_names, start=1):
                
                # Get the value in the cell
                value = int(row[col_class].strip())  
               
               # Diagonal (correct classification)
                if row_class == col_class:
                    diagonal.append((row_class, value))
                
                # Misclassification/wrong classification 
                else: 
                    if value > 0:
                        misclassifications[row_class].append((col_class, value))

        return diagonal, misclassifications



def per_class_misclassification(file_name):
    diagonal, misclassifications = get_misclassifications(file_name)

    if diagonal is None or misclassifications is None:
        print("Error retrieving data from the file.")
        return

    # Compare diagonal (correct classifications) with misclassifications
    print("Comparison of correct classifications and misclassifications:")
    

    for class_name, correct_count in diagonal:
        misclassified = misclassifications.get(class_name, [])
        total_misclassified = sum(count for _, count in misclassified)
        
        print(f"Class: {class_name}, Correct: {correct_count}, Misclassified: {total_misclassified}")

    # Print detailed misclassifications
    print("\nDetailed Misclassifications:")
    for class_name, misclassified in misclassifications.items():
        
        if misclassified:
            print(f"Class: {class_name}")
            
            for predicted_class, count in misclassified:
                print(f"  Predicted: {predicted_class}, Count: {count}")


if __name__ == "__main__":

#this is the csv file that contains the misclassification data  
    per_class_misclassification("Missclassifications_misclassifications.csv")
