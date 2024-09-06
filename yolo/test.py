from PIL import Image, ImageDraw, ImageFont
import numpy as np



def calculate_centroid(points):
    x = points[:, 0]
    y = points[:, 1]

    # Append the first point to the end to close the polygon
    x = np.append(x, x[0])
    y = np.append(y, y[0])

    # Calculate the signed area (A) of the polygon
    A = 0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])

    # Calculate the centroid coordinates (Cx, Cy)
    Cx = (1 / (6 * A)) * np.sum((x[:-1] + x[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1]))
    Cy = (1 / (6 * A)) * np.sum((y[:-1] + y[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1]))

    return Cx, Cy



def generate_arc_points(center, radius, start_angle, end_angle, num_points=100):
    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_points)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return list(zip(x, y))

def apply_scaling_and_translation(points, translation, scale, center):
    points = np.array(points)
    # Apply scaling (around the center)
    points = (points - center) * scale + center
    # Apply translation
    points += np.array(translation)
    return points

def apply_rotation(points, rotation, center):
    points = np.array(points)
    # Apply rotation (around the center)
    theta = np.radians(rotation)
    rotation_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
    points = np.dot(points - center, rotation_matrix) + center
    return points

def calculate_max_font_size(draw, text, font_path, shape_bounds, padding=20):
    max_width = shape_bounds[2] - shape_bounds[0] - 2 * padding
    max_height = shape_bounds[3] - shape_bounds[1] - 2 * padding
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    
    while True:
        text_width = draw.textlength(text, font=font)
        text_height = font_size
        if text_width > max_width or text_height > max_height or font_size > max_width or font_size > max_height:
            break
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    
    return max(1, font_size - 1)

def calculate_bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)
    return [min(x_coordinates), min(y_coordinates), max(x_coordinates), max(y_coordinates)]

def draw_shape(image_size, shape, translation=(0, 0), rotation=0, scale=1, fill_color=(255, 0, 0), text='A', font_path='arial.ttf', padding=20, cross_thickness=32):
    image = Image.new('RGB', image_size, (255, 255, 255))
    draw = ImageDraw.Draw(image)
    center = np.array(image_size) // 2
    radius = 160

    if shape == 'triangle':
        points = np.array([[-np.sqrt(3)/2 * 160, 160 / 2], [np.sqrt(3)/2 * 160, 160 / 2], [0, -160]]) + center
    elif shape == 'star':
        padding = 0
        points = np.array([[0, -160], [44, -48], [150, -48], [74, 22], [94, 128], 
                           [0, 80], [-94, 128], [-74, 22], [-150, -48], [-44, -48]]) + center
        inner_points = [points[i] for i in [1, 3, 5, 7, 9]]
    elif shape == 'rectangle':
        points = np.array([[-160, -80], [160, -80], [160, 80], [-160, 80]]) + center
    elif shape == 'pentagon':
        points = np.array([[0, -160], [150, -48], [94, 128], [-94, 128], [-150, -48]]) + center
    elif shape == 'circle':
        points = generate_arc_points(center, radius, 0, 360)
    elif shape == 'quarter-circle':
        adjusted_center = (center[0] - radius // 2, center[1] + radius // 2)
        p1 = (adjusted_center[0] + radius, adjusted_center[1])
        p2 = (adjusted_center[0], adjusted_center[1] - radius)
        p3 = adjusted_center
        arc_points = generate_arc_points(p3, radius, 0, -90)
        points = [p1] + arc_points + [p2, p3]
    elif shape == 'semi-circle':
        adjusted_center = (center[0], center[1] + radius // 2)
        arc_points = generate_arc_points(adjusted_center, radius, 180, 360)
        points = [(adjusted_center[0] - radius, adjusted_center[1])] + arc_points + [(adjusted_center[0] + radius, adjusted_center[1])]
    elif shape == 'cross':
        cross_thickness = 100
        padding = 0
        half_thickness = cross_thickness // 2
        points = np.array([[-160, -half_thickness], [-half_thickness, -half_thickness], [-half_thickness, -160], 
                           [half_thickness, -160], [half_thickness, -half_thickness], [160, -half_thickness], 
                           [160, half_thickness], [half_thickness, half_thickness], [half_thickness, 160], 
                           [-half_thickness, 160], [-half_thickness, half_thickness], [-160, half_thickness]]) + center
        inner_points = [points[i] for i in [1, 4, 7, 10]]
    else:
        raise ValueError("Shape not recognized")


    # Rotate shape
    points = apply_rotation(points, rotation, center)
    if shape in ['star', 'cross']:
        inner_points = apply_rotation(inner_points, rotation, center)

    # Apply scaling and translation
    points = apply_scaling_and_translation(points, translation, scale, center)
    if shape in ['star', 'cross']:
        inner_points = apply_scaling_and_translation(inner_points, translation, scale, center)


    if len(points) >= 3:
        draw.polygon([tuple(p) for p in points], fill=fill_color)

    if shape in ['star', 'cross']:
        shape_bounds = calculate_bounding_box(inner_points)
    else:
        shape_bounds = calculate_bounding_box(points)

    centroid = calculate_centroid(points)
    print(f'Centroid {centroid}')
    image = place_font_on_target(image, 'F', 'arial.ttf', 100, translation, rotation, scale, centroid)


    return image, points, centroid

def place_font_on_target(image, char, font_family, font_size, translation, angle, scale, centroid):  
    image_base =  image
    draw = ImageDraw.Draw(image_base)
    width, height = image_base.size
    true_font_height = font_size * scale
    font = ImageFont.truetype(font_family, true_font_height)
    font_width = font.getlength(char)
    font_image_canvas = Image.new('RGBA', (int(true_font_height), int(true_font_height)), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(font_image_canvas)
    font_image_width, font_image_height = font_image_canvas.size
    center_x, center_y = (font_image_width // 2, font_image_height // 2)
    draw2.text((center_x, center_y), char, font=font, anchor="mm", fill="black")
    font_image_canvas = font_image_canvas.rotate(angle)
    """x_offset = translation[0]-font_image_height//2
    y_offset = translation[1]-font_image_height//2
    if translation[0] == 0:
        x_offset = 0
    if translation[0] < 0:
        x_offset = translation[0]+font_image_height//2
    if translation[0] > 0:
        x_offset = translation[0]+font_image_height//2
    if translation[1] == 0:
        y_offset = 0
    if translation[1] < 0:
        y_offset = translation[1]+font_image_height//2
    """ 
    #image_base.paste(font_image_canvas, (int(centroid[0] -font_image_height//2) + x_offset, int(centroid[1]-font_image_height//2)+y_offset), font_image_canvas)
    image_base.paste(font_image_canvas, (int(centroid[0] -font_image_height//2), int(centroid[1]-font_image_height//2)), font_image_canvas)
    image_base.show()
    return image_base

def test_all_shapes(image_size, font_path):
    shapes = ['triangle', 'star', 'rectangle', 'pentagon', 'circle', 'quarter-circle', 'semi-circle', 'cross']
    
    transformations = [
        {'translation': (50, 50), 'rotation': 45, 'scale': 1, 'description': 'Translation (50, 50), Rotation 45°'},
        {'translation': (-100, -50), 'rotation': 90, 'scale': 1, 'description': 'Translation (-100, -50), Rotation 90°'},
        {'translation': (0, 0), 'rotation': 180, 'scale': 1, 'description': 'Rotation 180°'},
        {'translation': (-50, 100), 'rotation': 270, 'scale': 1, 'description': 'Translation (-50, 100), Rotation 270°'},
        {'translation': (20, -30), 'rotation': 135, 'scale': 1, 'description': 'Translation (20, -30), Rotation 135°'}
    ]
    
    for shape in shapes:
        for i, transform in enumerate(transformations):
            print(f"Testing shape: {shape}, Transformation {i+1}: {transform['description']}")
            image, points_str = draw_shape(
                image_size, 
                shape, 
                translation=transform['translation'], 
                rotation=transform['rotation'], 
                scale=transform['scale'], 
                fill_color=(255, 0, 0), 
                text='A', 
                font_path=font_path, 
                padding=20, 
                cross_thickness=32
            )
            image.show()
            print(f"Shape: {shape}, Transformation: {transform['description']}")

image_size = (3840, 2180)
font_path = "arial.ttf"
shape = "quarter-circle"


test, points, centroid = draw_shape(
    image_size,
    shape,
    translation = (100,100),
    rotation=75,
    scale=2,
    fill_color=(255,0,0),
    text="A",
    font_path=font_path,
    padding=20,
    cross_thickness=32
)
print(points)
for p in points:
    print(f'{p[0]/image_size[0]} {p[1]/image_size[1]}', end=" ")
test.show()
test.save('test.png')
print()
"""
print(np.min(points[:, 0])/image_size[0])
print(np.min(points[:, 1])/image_size[1])
print((np.max(points[:, 0])/image_size[0]-np.min(points[:, 0])/image_size[0]))
print(np.max(points[:, 1])/image_size[1]-np.min(points[:, 1])/image_size[1])
print(centroid[0]/image_size[0], centroid[1]/image_size[1])
"""
min_x = np.min(points[:, 0])/image_size[0]
max_x = np.max(points[:, 0])/image_size[0]
min_y = np.min(points[:, 1])/image_size[1]
max_y = np.max(points[:, 1])/image_size[1]
print(f"0 {(max_x+min_x)/2} {(max_y+min_y)/2} {max_x-min_x} {max_y-min_y}")