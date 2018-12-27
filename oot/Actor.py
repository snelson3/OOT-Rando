from .Utils import toHex

class Actor():
    def __init__(self, accessor, num, offset, var=0):
        self.accessor = accessor
        self.num = num
        self.var = var
        self.offset = offset # What offset is the actor in the actor list
        self.filename = self.lookupFilename()
        self.object_name, self.description = self.matchObject()
    def getInfo(self):
        return "{}) {} {} ({}) [{}] -> {}".format(self.offset, self.num, self.filename, self.description, self.var, self.object_name)
    def lookupFilename(self):
        return self.accessor.reader.lookupActorFieldByIndex(self.num, 'Filename')
    def lookupInitVars(self):
        return self.accessor.reader.lookupActorFieldByIndex(self.num, 'Init Vars')
    def lookupRAMStart(self):
        return self.accessor.reader.lookupActorFieldByIndex(self.num, 'VRAM Start')
    def lookupROMStart(self):
        return self.accessor.reader.lookupActorFieldByIndex(self.num, 'VROM Start')
    def matchObject(self):
        if self.accessor.cache_enabled and self.filename in self.accessor.cache.actor_object_cache:
            return self.accessor.cache.actor_object_cache[self.filename]["name"], self.accessor.cache.actor_object_cache[self.filename]["description"]
        else:
            if self.filename in ['En_A_Obj', 'En_Item00']:
                objId = '0001' # These objects need a special case
            else:
                objId_address = int(self.lookupROMStart(),16) + int(self.lookupInitVars(),16) - int(self.lookupRAMStart(),16) + 8
                objId = ''.join([toHex(b) for b in self.accessor.getData(objId_address, objId_address +2)])
            if objId not in self.accessor.reader.getObjectNames():
                return "NA", ""
            row = self.accessor.reader.lookupObjectByIndex(objId)
            info = {"name": row['Filename'], "description":row['Description']}
            self.accessor.cache.actor_object_cache[self.filename] = info
        return info["name"], info["description"]
    def setObject(self, fn):
        if fn in self.accessor.cache.actor_object_cache:
            object_info = self.accessor.cache.actor_object_cache[fn]
        else:
            object_info = {"name": fn, "description": self.accessor.reader.lookupObjectDescription(fn)}
        self.object_name = object_info["name"]
        self.description = object_info["description"]