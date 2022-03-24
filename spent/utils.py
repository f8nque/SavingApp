import uuid

def generateUUID():
    code = str(uuid.uuid4()).replace('-','')
    return code

class TrackingDict:
    def __init__(self):
        self.tracking_dict = {}
    def addCategory(self,category,id):
        self.tracking_dict[category] = [id,0]
    def updateCategory(self,category):
        self.tracking_dict[category][1] = 1
    def get_tracking_list(self):
        return self.tracking_dict