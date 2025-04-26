
import csv
import os

# Needs to be installed 
#All these imports are for the matrix
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import confusion_matrix 
import pandas as pd 


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

#This function is the breakdown of the csv file # values and the correct as well as misclassification
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

    
    #This part of the code is only for the confusion matrix
    df = pd.read_csv(file_name, index_col=0)

    # Clean up any extra spaces from rows and columns
    df.index = df.index.str.strip()
    df.columns = df.columns.str.strip()

    # Select only specific classes you want to plot (I did all for now) 
    classes_to_plot = ['person', 'motorcycle', 'car', 'airplane', 'bus', 'boat', 'stop_sign', 'snowboard', 'umbrella', 'sports_ball', 'baseball_bat', 'bed', 'tennis_racket', 'suitcase']

    # Slice the dataframe to keep only the selected classes
    small_df = df.loc[classes_to_plot, classes_to_plot]

    # Prepare the small matrix and labels
    matrix = small_df.values
    labels = small_df.columns

    # Plot the smaller confusion matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels)
        
    # optional (color map for better visuals) has a default
    disp.plot(cmap='cool')  
       
    #This is the title of the matrix
    plt.title('Confusion Matrix')
        
    #Contols the rotation of the labels to aviod overlap and aligns them to the right 
    plt.xticks(rotation=45, ha='right')
       
    #aviods things form being cut out on the pop up window
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":

#this is the csv file that contains the misclassification data
# make sure to change this file 
    per_class_misclassification("Missclassifications_misclassifications.csv")
    
