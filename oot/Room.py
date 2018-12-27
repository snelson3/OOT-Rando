from .globals import *
from .Actor import Actor
from .ZObject import ZObject
from .Utils import toHex

class Room():
    def __init__(self, accessor, addr, fn, descr=''):
        self.accessor = accessor
        self.address = addr
        self.fn = fn
        self.descr = descr
        self.setups = {}
        self.setups[0] = self.getSceneSetup(self.accessor.createRoomHeader(self.address))
        alternateSetupAddrs = self.setups[0]['header'].getAlternateHeaders()
        if alternateSetupAddrs:
            for i, addr in enumerate(alternateSetupAddrs):
                self.setups[i+1] = self.getSceneSetup(self.accessor.createRoomHeader(addr, isHex=False))
    def getSceneSetup(self,header):
        object_list_addr = int(self.address, 16) + header.objectListDef['offset']
        actor_list_addr = int(self.address, 16) + header.actorListDef['offset']
        return {
            "header": header,
            "object_list_addr": object_list_addr,
            "objects": self.getObjects(object_list_addr, header.objectListDef['num']),
            "actor_list_addr": actor_list_addr,
            "actors": self.getActors(actor_list_addr, header.actorListDef['num'])
        }
    def getActors(self, addr, nactors):
        actor_list_data = self.accessor.getData(addr,addr+(nactors*ACTOR_REC_SIZE))
        actor_list = []
        for a in range(0, len(actor_list_data), ACTOR_REC_SIZE):
            var_offset = 14 # how many bytes into the actor_list_data is the variable
            actor_num = ''.join([toHex(b) for b in actor_list_data[a:a+2]])
            variable = ''.join([toHex(b) for b in actor_list_data[a+var_offset:a+var_offset+2]])
            actor = Actor(self.accessor, actor_num, a // ACTOR_REC_SIZE, var=variable)
            actor_list.append(actor)
        return actor_list
    def getObjects(self, addr, numobjects):
        object_list_data = self.accessor.getData(addr,addr+(numobjects*OBJECT_REC_SIZE))
        object_list = []
        for o in range(0, len(object_list_data), OBJECT_REC_SIZE):
            objId = ''.join([toHex(b) for b in object_list_data[o:o+2]])
            obj = ZObject(self.accessor, objId, o // OBJECT_REC_SIZE)
            object_list.append(obj)
        return object_list
    def hasObject(self, fn, setup):
        return fn in [o.filename for o in self.setups[setup]['objects']]
    def replaceObject(self, old_fn, new_fn, setup=0):
        roomSetup = self.setups[setup]
        for z in range(len(roomSetup['objects'])):
            zobj = roomSetup['objects'][z]
            if old_fn == zobj.filename:
                obj_addr = roomSetup['object_list_addr'] + zobj.offset*OBJECT_REC_SIZE
                newObj = ZObject(self.accessor, lookupObjectNum(new_fn), zobj.offset)
                self.accessor.setData(obj_addr, [int(newObj.objId[:2],16), int(newObj.objId[2:],16)])
                roomSetup['objects'][z] = newObj
    def replaceActor(self, old_fn, new_fn, new_var='0000', old_object_fn=None, new_object_fn=None, index=None, setup=0, replaceObject=True, absIndex=None):
        c = -1
        if not setup in self.setups:
            raise Exception("Trying to replace actor in nonexistent setup!")
        roomSetup = self.setups[setup]
        for a in range(len(roomSetup['actors'])):
            if absIndex != None and a != absIndex:
                continue
            actor = roomSetup['actors'][a]
            if actor.filename == old_fn:
                if index != None:
                    c += 1
                    if index != c:
                        continue
                actor_addr = roomSetup['actor_list_addr'] + actor.offset*ACTOR_REC_SIZE
                # lookupActor should be used by getActors
                newActor = Actor(self.accessor, self.accessor.reader.lookupActorNum(new_fn), actor.offset, new_var)
                if old_object_fn:
                    actor.setObject(old_object_fn)
                if new_object_fn:
                    newActor.setObject(new_object_fn)
                if actor.object_name == 'NA' and replaceObject:
                    raise Exception("Old Actor's Corresponding Object can't be identified")
                if newActor.object_name == 'NA' and replaceObject:
                    raise Exception("New Actor's Corresponding Object can't be identified")
                # This seems stupid, why am I converting the num to hex to convert back to dec
                # Should be a method in the Actor class for setting the data to what's stored in the class
                self.accessor.setData(actor_addr, [int(newActor.num[:2], 16), int(newActor.num[2:], 16)])
                var_offset = 14 # how many bytes into the actor_list_data is the variable
                self.accessor.setData(actor_addr+var_offset, [int(newActor.var[:2], 16), int(newActor.var[2:], 16)])
                def _associatedWithBaseObject(actor):
                    return actor.object_name in ['gameplay_keep', 'gameplay_field_keep', 'gameplay_dangeon_keep']
                if replaceObject and not _associatedWithBaseObject(newActor) and not self.hasObject(newActor.object_name, setup):
                    self.replaceObject(actor.object_name, newActor.object_name, setup=setup)
                roomSetup['actors'][a] = newActor
                if index != None:
                    return
    def getInfo(self, setupNum=None):
        def _getInfoForSetup(num):
            global x
            x = self.setups[num]
            return '\n'.join([
                '{} ({}) setup {} @ {}'.format(self.fn, self.descr, num, self.setups[num]['header'].start_addr),
                '### Objects ###',
                *[o.getInfo() for o in self.setups[num]['objects']],
                '### Actors ###',
                *[a.getInfo() for a in self.setups[num]['actors']]
            ])
        if not setupNum:
            return '\n\n'.join([_getInfoForSetup(i) for i in self.setups])
        return self.setups[setupNum]