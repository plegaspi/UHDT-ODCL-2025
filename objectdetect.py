def adjust_bbox(bb, padding, img_width, img_height):
    x_min, y_min, x_max, y_max = bb
    while True:
        new_x_min = max(x_min - padding, 0)
        new_y_min = max(y_min - padding, 0)
        new_x_max = min(x_max + padding, img_width)
        new_y_max = min(y_max + padding, img_height)

        if new_x_min == x_min and new_y_min == y_min and new_x_max == x_max and new_y_max == y_max:
            break

        x_min, y_min, x_max, y_max = new_x_min, new_y_min, new_x_max, new_y_max
        padding -= 1

    return (new_x_min, new_y_min, new_x_max, new_y_max)