
from enum import Enum

class ModeOfTransport(Enum):
    DRIVE = 'drive'
    WALK = 'walk'
    TRANSIT = 'transit'

class PoiDefinition:
    def __init__(self, title="", mode_of_transport=ModeOfTransport.WALK, minutes_table=0, address="", isolineObject=[], filtered=False):
        self.title = title
        self.mode_of_transport = mode_of_transport
        self.minutes_table = minutes_table
        self.address = address
        self.isolineObject = isolineObject
        self.filtered = filtered