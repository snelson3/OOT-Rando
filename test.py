from oot.oot import Oot
from oot.Accessor import Accessor
import os, random, requests, time

CACHE_ENABLED = True
SEED = None
LOGDIR = 'logs'
GAMEDIR = 'roms'
game = Oot(gamedir=GAMEDIR, logdir=LOGDIR)
accessor = Accessor(game)

# Cell for testing individual actor replacements
# Kokiri main spot04_room_0
# To replace rock guy old_actor=En_Ko, old_object_fn=object_km1
# Mido's House kokiri_home4_room_0
accessor.readData()
accessor.replaceActorInRoom('En_Tite', 'En_Box', 'MIZUsin_room_0', var='00FF')
#replaceActorInRoom('En_Box', 'En_Box', 'kokiri_home4_room_0', var='0700')
#replaceActorInRoom('En_Ko', 'En_Rr', 'spot04_room_0', var='0003', index=0, old_object_fn='object_os_anime')
#replaceActorInRoom('En_Karebaba', 'En_Skj', 'spot04_room_1', var='FFFF', old_object_fn='object_dekubaba')
accessor.spawnAt(0x5)
accessor.writeData()