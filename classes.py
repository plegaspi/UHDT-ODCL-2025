class Target:
    def __init__(self, predicted_classes, confidence_scores, latitude=None, longitude=None):
        self.predicted_classes = predicted_classes
        self.confidence_scores = confidence_scores
        self._latitude = None  # Use a private variable
        self._longitude = None
        self._num_payloads = 0

        if latitude is not None:
            self.latitude = latitude 
        if longitude is not None:
            self.longitude = longitude

        if latitude is not None:
            self.latitude = latitude 
        if longitude is not None:
            self.longitude = longitude  

    def validate_latitude(self, latitude):
        if latitude is None:
            raise ValueError("Latitude cannot be None")
        if not isinstance(latitude, (int, float)):
            raise TypeError("Latitude must be a number")
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return latitude
    
    def validate_longitude(self, longitude):
        if longitude is None:
            raise ValueError("Longitude cannot be None")
        if not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be a number")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return longitude

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        self._latitude = self.validate_latitude(latitude)

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter    
    def longitude(self, longitude):
        self._longitude = self.validate_longitude(longitude)

    @property
    def num_payloads(self):
        return self._num_payloads

    @num_payloads.setter
    def num_payloads(self, num_payloads):
        if num_payloads < 0:
            raise ValueError("Payloads cannot be negative")
        self._num_payloads = num_payloads