class Detection():
    def __init__(self, classifications, confidences, coordinates, original_image, cropped_image):
        self.classifications = classifications
        self.confidences = confidences
        self.coordinates = coordinates
        self.original_image = original_image
        self.cropped_image = cropped_image


class Target():
    def __init__(self, name):
        self.name = name
        self.coordinates = ()
        number_of_payloads = 0

    def set_number_of_payloads(self, number_of_payloads):
        self.number_of_payloads = number_of_payloads

    def set_coordinates(self, coordinates):
        self.coordinates = coordinates