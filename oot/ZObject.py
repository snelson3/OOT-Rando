class ZObject(): # This object is related to the object instance in a room, not to a specific kind of object
    def __init__(self, accessor, num, offset):
        self.accessor = accessor
        self.objId = num
        self.offset = offset # What offset is the object in the object list
        self.filename = self.lookupFilename()
        self.description = self.lookupDescription()
    def getInfo(self):
        return "{}) {} {} ({})".format(self.offset, self.objId, self.filename, self.description)
    def lookupFilename(self):
        return self.accessor.reader.lookupObjectFieldByIndex(self.objId, 'Filename')
    def lookupDescription(self):
        return self.accessor.reader.lookupObjectFieldByIndex(self.objId, 'Description')