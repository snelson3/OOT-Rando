from oot.oot import Oot
from oot.Accessor import Accessor
import os, random, requests, time

CACHE_ENABLED = True
SEED = None
LOGDIR = 'logs'
GAMEDIR = 'roms'
game = Oot(gamedir=GAMEDIR, logdir=LOGDIR)
accessor = Accessor(game)

accessor.readData()
rooms_list = accessor.reader.getRoomNames()
rooms = accessor.generateRooms(rooms_list)
accessor.spawnAt(0x56)
accessor.writeData()