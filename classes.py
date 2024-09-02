class Target:
    def __init__(self, shape = "default", latitude = 38.3143415, longitude = -76.5441875, shapeColor = "default", alphanumColor = "default", alphanum = "default"):
        self.shape = shape
        self.latitude = latitude
        self.longitude = longitude
        self.shapeColor = shapeColor
        self.alphanumColor = alphanumColor
        self.alphanum = alphanum

class Payload:
    def __init__(self, dock, shape, shapeColor, alphanumColor, alphanum):
        self.dock = dock
        self.shape = shape
        self.shapeColor = shapeColor
        self.alphanumColor = alphanumColor
        self.alphanum = alphanum