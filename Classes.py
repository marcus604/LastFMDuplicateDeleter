
class Scrobble:
    
    def __init__(self, artist, title, timestamp):
        #Config
        self.artist = artist
        self.title = title
        self.timestamp = timestamp
       

    def __str__(self):
        return "{}: {} - {}".format(self.timestamp, self.artist, self.title)
    
    def print(self):
        print("{}: {} - {}".format(self.timestamp, self.artist, self.title))
        

class Config_Exception(Exception):
    pass







