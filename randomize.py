from oot.oot import Oot
from oot.Accessor import Accessor
import os, random, requests, time
from oot.Utils import *

##### DEFINE SETTINGS
FORCE_ASSUMPTIONS = True
SEED = 'Deadpool2'
ROM = "ZOOTDEC.z64"
#TODO SELECTEDENEMY WON"T WORK DUE TO ISSUE IN logicmanager.getNewActor
SELECTED_ENEMY = None #{'fn': 'En_Dodojr', 'object_fn': 'object_dodojr', 'var': ('0000', '')}
game = Oot(fn=ROM)
accessor = Accessor(game, force_assumptions=FORCE_ASSUMPTIONS, selected_enemy=SELECTED_ENEMY)
accessor.spawnAt(0x3)
#####

start_time = time.time()
seed = SEED if SEED else str(start_time)
setSeed(seed)
print("Seed: {}".format(seed) )

accessor.readData()
print("Data read, {} sec".format(time.time()-start_time))

rooms_list = accessor.reader.getRoomNames()
rooms = accessor.generateRooms(rooms_list)
print("Room Info Generated, {} sec".format(time.time()-start_time))

spoilers = {}
# TODO move spoilers into accessor, and have auto filled out
# OOT is made up of a bunch of rooms, loop through them
for r, room in rooms.items():
    # Most rooms have multiple setups, IE 1 for Adult 1 for Kid
    for n, setup in room.setups.items():
        ## Some housekeeping, link all the enemy actor instances to their object instance
        ## TODO Move to room setup or tear out
        for actor in setup['actors']:
            if not accessor.reader.isEnemy(actor_name=actor.filename):
                continue
            actor.setObject(accessor.reader.lookupEnemyFieldByName("Object FN", actor_name=actor.filename))
        setup_spoiler = {'objects':[],'actors':[]}
        _getRoomName = lambda r,n: '{}-{} ({})'.format(r,n,room.descr)
        spoilers[_getRoomName(r,n)] = setup_spoiler
        possible_objects = [o for o in setup['objects'] if accessor.manager.canRandomizeObject(o, setup['actors'])]
        for obj in possible_objects:
            new_obj = accessor.manager.getNewObject(obj, setup['actors'])
            room.replaceObject(obj.filename, new_obj, n)
            setup_spoiler['objects'].append({'old': obj.filename, 'new': new_obj})
        for actor in setup['actors']:
            # Some rooms have multiples of the same actor, so come up with an index of them
            # TODO this should be an attribute in the Actor class that is filled in on init
            index = [i for i in setup['actors'] if i.filename == actor.filename].index(actor)
            if accessor.manager.canRandomizeActor(actor):
                new_actor, new_var = accessor.manager.getNewActor(actor, possible_objects)
                setup_spoiler['actors'].append({'old': actor.filename, 'new': new_actor, 'old_var': actor.var, 'new_var': "({}, {})".format(new_var.var,new_var.desc)})
                room.replaceActor(actor.filename, new_actor, new_var=new_var.var, index=index, setup=n, replaceObject=False)
print("Rooms Randomized, {} sec".format(time.time()-start_time))

# Print out spoilers
accessor.writeEnemySpoilers(spoilers, "spoiler.log")
print("Replacement Log Written".format(time.time()-start_time))

accessor.writeData()
print("New ROM Written {}".format(time.time()-start_time))