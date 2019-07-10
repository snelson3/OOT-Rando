from .randoassist.Randomizer import Randomizer
from .randoassist.RandUtils import RandUtils
ru = RandUtils()
import os, random, subprocess, shutil

# http://wiki.spinout182.com/w/Ocarina_of_Time:_Entrance_Table
ENTRANCE_TABLE = 0x00B6FBF0
ENTRANCE_TABLE_SIZE = 1555*4 # Records * bytes per record

class Oot(Randomizer):
    def __init__(self, gamedir, logdir='.', fn="ZOOTDEC.z64"):
        Randomizer.__init__(self, logdir=logdir)
        self.gamedir = gamedir
        self.fn = fn
        self.readData()
    def readData(self):
        self.data = self.getData()
    def getData(self):
        fn = os.path.join(self.gamedir, self.fn)
        if not os.path.isfile(fn):
            raise Exception("Expanded rom {} not found".format(fn))
        with open(fn, "rb") as f:
            print("reading {}".format(fn))
            return bytearray(f.read())
    def process(self):
        if not self.args:
            raise Exception("No Arguments Set")
        if "triforce-transitions" in self.args:
            self.addTriforceTransitions()
        if "entrances" in self.args:
            self.randomizeEntrances()
        if "actors" in self.args:
            self.randomizeActors()
        if "rebuild" in self.args or "build" in self.args:
            pass
    def create(self, data=None, fn="NEWZOOT.z64"):
        game_fn = os.path.join(self.gamedir,fn)
        self.log.output("Writing {}".format(game_fn))
        with open(game_fn, "wb") as f:
            f.write(self.data if not data else data)
    def addTriforceTransitions(self):
        for b in range(ENTRANCE_TABLE-1+24, ENTRANCE_TABLE+ENTRANCE_TABLE_SIZE, 4):
            self.data[b+4] = 1
    def randomizeEntrances(self):
        entrance_indexes_to_ignore = [
            (int(i,16)*4)+ENTRANCE_TABLE for i in [
            '0014', # Lost Scene
            '0015',
            '0016',
            '0017',
            '0018', # Action Testing Room
            '0019',
            '001A',
            '001B',
            '001C', # Stalfos Middle Room
            '001D',
            '001E',
            '001F',
            '0020', # Stalfos Boss Room
            '0021',
            '0022',
            '0023',
            '0024', # Item Testing Room
            '0025',
            '0026',
            '0027',
            '0047', # Dark Link Testing Area
            '0048',
            '0049',
            '004A',
            '006B', # Chamber of Sages
            '006C',
            '006D',
            '006E',
            '006F',
            '0070',
            '0071',
            '0076', # Beta Castle Courtyard
            '0077',
            '0078',
            '0079',
            '0094', # Collision Testing Arena
            '0095',
            '0096',
            '0097',
            '00A0', # Cutscene Map
            '00A1',
            '00A2',
            '00A3',
            '00A4',
            '00A5',
            '00A6',
            '00A7',
            '00A8',
            '00A9',
            '00AA',
            '00AB',
            '00AC',
            '00B6', # Depth Test
            '024E', # Outside Boss Door, from Forest Temple Boss, Secret Map #0
            '024F',
            '0250',
            '0251',
            '0282', # Hyrule Field, Unused Location
            '0283',
            '0284',
            '0285',
            '02B6', # From Shadow Temple Boss, Secret Map #0
            '02B7',
            '02B8',
            '02B9',
            '02CE', # Chamber of Sages
            '02CF',
            '02D0',
            '02D1',
            '02EF', # Cutscene Map
            '0369', # Haunted Wasteland Crashes (Bad Map)
            '036A',
            '036B',
            '036C',
            '03E8', # Kakariko Potion Shop Unused
            '03E9',
            '03EA',
            '03EB',
            '03F8', # Spirit Temple (Crashes Bad Map)
            '03F9',
            '03FA',
            '03FB',
            '0480', # Ganons Castle (Crashes Bad Map)
            '0481',
            '0520', # Beshitu
            '0521',
            '0522',
            '0523',
        ]]
        # I probably want to leave all the cutscene records alone, which means I should only randomize among the first 4
        def _ignoreRecord(b):
            return b in entrance_indexes_to_ignore #or b <= ENTRANCE_TABLE+1000
        def _cutsceneRecord(b):
            # if the 4 previous records all contain the same scene/entrance values, the record is used for cutscenes
            # if b == ENTRANCE_TABLE+50*4:
            #     print(self.data[b-16:b-14])
            #     print(self.data[b-12:b-10])
            #     print(self.data[b-8:b-6])
            #     print(self.data[b-4:b-2])
            #     print(self.data[b:b+2])
            return self.data[b-16:b-14] == self.data[b-12:b-10] == self.data[b-8:b-6] == self.data[b-4:b-2] == self.data[b:b+2]
        possible_entrances = []
        for b in range(ENTRANCE_TABLE, ENTRANCE_TABLE+ENTRANCE_TABLE_SIZE, 4):
            if not _ignoreRecord(b):
                if not _cutsceneRecord(b):
                    possible_entrances.append((self.data[b], self.data[b+1]))
                    continue
                entrance_indexes_to_ignore.append(b)
        print("{} entrances being shuffled".format(len(possible_entrances)))
        random.shuffle(possible_entrances)
        for b in range(ENTRANCE_TABLE, ENTRANCE_TABLE+ENTRANCE_TABLE_SIZE, 4):
            if not _ignoreRecord(b):
                ent = possible_entrances.pop()
                self.data[b] = ent[0]
                self.data[b+1] = ent[1]
    def randomizeActors(self):
        pass
    def set_bytes(self, start_address, values):
        for i, value in enumerate(values):
            self.set_byte(start_address+i, value)
    def set_byte(self, address, value):
        self.data[address] = value



if __name__ == "__main__":
    rand = Oot()
    rand.process()
    rand.create()