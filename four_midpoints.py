# Function to generate plot
import matplotlib.pyplot as plt
def plot_points(coords):
    # Extract x and y values from the coordinates
    x_values = [coord[0] for coord in coords]
    y_values = [coord[1] for coord in coords]
    plt.style.use('grayscale')
    # Create the plot
    plt.figure(figsize=(7, 7))
    plt.scatter(x_values, y_values, color='blue', label='Points')  # Scatter plot for points    
    # Annotate each point
    for i, coord in enumerate(coords):
        plt.text(coord[0]+0.1, coord[1], f'{coord}', fontsize=6)
    # Set plot labels and grid
    plt.margins(0.1)
    plt.title('Coordinates')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True, which='both', linestyle='-', linewidth=0.5, alpha=0.3)
    plt.xticks(fontsize=7)
    plt.yticks(fontsize=7)
    plt.show()

# Function to sort coordinates
def sort_coordinates(coordinates):
    # Sort by y-coordinate in descending order, then by x-coordinate in ascending order
    sorted_by_y = sorted(coordinates, key=lambda coord: (-coord[1], coord[0]))
    
    # Take the two highest points and the two lowest points
    highest_points = sorted_by_y[:2]  # First two points (highest y-values)
    lowest_points = sorted_by_y[2:]   # Remaining two points (lowest y-values)
    
    # Sort each group by x-coordinate (left to right)
    highest_points_sorted = sorted(highest_points, key=lambda coord: coord[0])
    lowest_points_sorted = sorted(lowest_points, key=lambda coord: coord[0])
    
    # Combine the sorted groups
    result = highest_points_sorted + lowest_points_sorted
    return result

#function to get the four midpoints
def four_midpoints(coordinates):
    x_coord = [coords[0] for coords in coordinates]
    y_coord = [coords[1] for coords in coordinates]
    # Calculate the averages
    midpoint_x = sum(x_coord) / 4
    midpoint_y = sum(y_coord) / 4
    fourmids = []
    # Calculate the average between the midpoint and each of the four corners
    for i in range(len(coordinates)):
        x = int(coordinates[i][0])
        y = int(coordinates[i][1])
        xave = (midpoint_x + x) / 2
        yave = (midpoint_y + y) / 2
        mids = (xave,yave)
        fourmids.append(mids)
    return (fourmids)


if __name__ == '__main__':
    #coords = [(1, 1), (1, 5), (5, 1), (5, 5)]
    #coords = [(1, 1), (1, 5), (5, 3), (5, 7)]
    coords = [(0,2),(2,0),(4,2),(2,4)]
    sorted_coords = sort_coordinates(coords)
    midpoints = four_midpoints(sorted_coords)
    print("Sorted coordinates:", sorted_coords)
    print("midpoints",midpoints)
    plot_points(sorted_coords + midpoints)
