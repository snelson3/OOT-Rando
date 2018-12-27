from .DataReader import PandasDataReader
from .Room import Room
from .Header import Header
from collections import namedtuple

class Accessor:
    def __init__(self, game):
        self.game = game
        self.reader = PandasDataReader()
        self.cache_enabled = True
        Cache = namedtuple('Cache', 'actor_object_cache')
        self.cache = Cache(actor_object_cache={})
    def readData(self):
        self.game.readData()
    def getData(self, start, end=None, to_end=False, size=None):
        if to_end:
            return self.game.data[start:]
        if not end:
            if size:
                end = start+size
            else:
                return self.game.data[start]
        return self.game.data[start:end]
    def setData(self, addr, barr):
        self.game.set_bytes(addr, barr)
    def writeData(self):
        self.game.create()
    def searchData(self, st):
        # Search the ROM for instances of the above string of hex bytes, with * as a wildcard character
        # Return a list of hex addresses that match
        # '01 B9 FE B6 01 E0 F7 04'
        foundInsts = []
        bytelist = [int(b,16) if b != '*' else '*' for b in st.split(' ')]
        for b in range(len(game.data)):
            instFound = True
            for c in range(len(bytelist)):
                if bytelist[c] == '*' or bytelist[c] == self.game.data[b+c]:
                    continue
                instFound = False
                break
            if instFound:
                foundInsts.append(hex(b))
        return foundInsts
    def createRoomByName(self, name):
        record = self.reader.ref.files.loc[name]
        return Room(self, record['VROM Start'], name, record['Contents'])
    def createRoomHeader(self, addr, isHex=True):
        # used to be called lookupRoomHeader
        dec_addr = int(addr, 16) if isHex else addr 
        return Header(self, dec_addr)
    def getRoomHeaderByName(self, name):
        return self.createRoomHeader(self.reader.getRoomAddrByName(name))
    def generateRooms(self, names):
        return {n: self.createRoomByName(n) for n in names}
    def replaceActorInRoom(self, old, new, room_name, var='0000', old_object_fn=None, new_object_fn=None, index=None):
        self.createRoomByName(room_name).replaceActor(old,new, var, old_object_fn=old_object_fn, new_object_fn=new_object_fn, index=index)
    def listActorInformation(self, fn):
        found_info = {}
        rooms = self.generateRooms(self.getRoomNames())
        for name, room in rooms.items():
            for num, setup in room.setups.items():
                actors = [a for a in setup['actors'] if a.filename == fn]
                if len(actors) > 0:
                    found_info['{}-{} ({})'.format(name, num, room.descr)] = actors
        for room, actors in found_info.items():
            print(room)
            for actor in actors:
                print(actor.getInfo())
    def spawnAt(self, scene, entrance=0x0):
        # Changes the spawn location for kid link (out of dungeons) to the specified record no (as a string)
        ent_table = 0x00B6FBF0 # Start of entrance table
        links_house_ent = ent_table+(4*0xBB) # Record No of the entrance to 
        self.setData(links_house_ent, [scene, entrance])