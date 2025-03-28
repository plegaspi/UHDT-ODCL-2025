
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
def defaultdropcoordinates(coordinates):
    long = [coords[0] for coords in coordinates]
    lat = [coords[1] for coords in coordinates]
    # Calculate the averages
    midpoint_long = sum(long) / 4
    midpoint_lat = sum(lat) / 4
    print(midpoint_long,midpoint_lat)
    defaultdropcoords = []
    # Calculate the average between the midpoint and each of the four corners
    for i in range(len(coordinates)):
        x = (coordinates[i][0])
        y = (coordinates[i][1])
        xave = (midpoint_long + x) / 2
        yave = (midpoint_lat + y) / 2
        mids = (xave,yave)
        defaultdropcoords.append(mids)
    return (defaultdropcoords)


if __name__ == '__main__':
    coords = [(21.399622, 157.766405), (21.400889, 157.765178), (21.400416,157.763620), (21.401183, 157.764038)]
    sorted_coords = sort_coordinates(coords)
    midpoints = defaultdropcoordinates(sorted_coords)
    print("Sorted coordinates:", sorted_coords)
    print("midpoints",midpoints)
