from oot.oot import Oot
from oot.Accessor import Accessor
from oot.Utils import setSeed
import os, random, requests, time

CACHE_ENABLED = True
SEED = None
LOGDIR = 'logs'
GAMEDIR = 'roms'
game = Oot(gamedir=GAMEDIR, logdir=LOGDIR)
accessor = Accessor(game)

### Cell to randomize enemies ONLY
start_time = time.time()
SEED = 91542915092.487943#'Winnie'
seed = SEED if SEED else str(start_time)
setSeed(seed)
print("Seed: {}".format(seed) )
selected_enemy = None#{'fn': 'En_Torch2', 'object_fn': 'object_torch2', 'var': ('FFFF', '')} # Mostly for debug will change all enemies to this type

def _readVars(string):
    if len(string) < 2:
        return []
    return map(lambda x: x.strip(), string.split(","))

enemies = {}
for enemy in accessor.reader.getEnemyIndex()[1:]:
    enemy_info = accessor.reader.lookupEnemyByIndex(enemy)
    if enemy_info['Enabled']:
        key = enemy_info['Requirements']
        if enemy_info['Requirements'] not in enemies:
            enemies[key] = {}
        # Variables are of the form 'XXXX (), '
        variables = enemy_info['Variable\'s'].split(',')
        variables = [v.split(' (') for v in variables]
        real_variables = []
        for v in variables:
            var = v[0].strip()
            if len(var) != 4: 
                raise Exception("Enemy {} has invalid variable {}".format(enemy, list(var)))
            descr = ''
            if len(v) > 1:
                descr = v[1].split(')')[0]
            real_variables.append((var,descr))
        # From Variables just a list of variables rather than having the description too
        from_variables = enemy_info['From-Var\'s']
        if len(from_variables) > 0:
            print(from_variables)
        enemies[key][enemy] = {
            "actor_fn": enemy_info['Actor FN'],
            "object_fn": enemy_info['Object FN'],
            "variables": real_variables,
            "from_variables": from_variables,
            "descr": descr,
            "type": key,
            "enemy": enemy
        }
        
available_actors = accessor.reader.getEnemyActorNames()
available_objects = accessor.reader.getEnemyObjectNames()

def isEnemyObject(st):
    return st in available_objects
def isEnemyActor(st):
    return st in available_actors
        
object_enemies = { k: [e["object_fn"] for e in v.values()] for k,v in enemies.items() }

actor_var_pairs = {}
from_actor_var_pairs = {}
for t,el in enemies.items():
    for e in el.values():
        for var in e["variables"]:
            actor_var_pairs['{}-{}'.format(e['actor_fn'], var[0])] = e
        for var in _readVars(e["from_variables"]):
            from_actor_var_pairs['{}-{}'.format(e['actor_fn'], var[0])] = e
print("enemy-type lists created: {}".format(time.time()-start_time))

accessor.readData()
print("Data read, {} sec".format(time.time()-start_time))

rooms_list = accessor.reader.getRoomNames()
rooms = accessor.generateRooms(rooms_list)
print("Room Info Generated, {} sec".format(time.time()-start_time))

# I think I can just assume that a object is only related to one actor in a room

# Once I have every actor linked to an object, it will be easier to have a way to look and see what actors are associated with an object
myx = None # Debug variable
def _getObjType(obj, actors, room):
    global myx
    # Find the actor that is associated with the object, and return that actors type
    for actor in actors:
        if actor.object_name == obj.filename:
            n = '{}-{}'.format(actor.filename,actor.var)
            if not n in actor_var_pairs:
                myx = (actor, obj, room, n)
                if not n in from_actor_var_pairs:
                    return False # don't randomize
                else:
                    return actor_var_pairs[n]['type'] # I think this works because the from vars enemies aren't in the main pool
            return actor_var_pairs[n]['type']
    return False#'dont-randomize' # object doesn't have a corresponding actor so it's probably dynamically generated. so don't randomize

def _getActorType(actor):
    return actor_var_pairs['{}-{}'.format(actor.filename, actor.var)]['type']
def _getObjs(tpe):
    return object_enemies[tpe]
def _getActors(tpe, objects):
    return [a for a in enemies[tpe].values() if a['object_fn'] in objects]
    # Return all the actors associated with those objects that match the given type
def _getAvailableActors(actor, possible_objects):
    t = _getActorType(actor)
    return [(a['actor_fn'], a['variables'], a['enemy']) for a in _getActors(t, possible_objects)] 
def _writeEnemySpoilers(spoilers, fn):
    fn = os.path.join(LOGDIR, fn)
    with open(fn, "w") as f:
        for name, setup in spoilers.items():
            if len(setup['objects']) > 0 or len(setup['actors']) > 0:
                f.write('{}\n'.format(name))
            if len(setup['objects']) > 0:
                f.write(' objects\n')
            for o in setup['objects']:
                f.write('  {} -> {}\n'.format(o['old'], o['new']))
            if len(setup['actors']) > 0:
                f.write(' actors\n')
            for a in setup['actors']:
                f.write('  {} [{}] -> {} [{}] ({})\n'.format(a['old'], a['old_var'], a['new'], a['new_var'], a['descr']))
    pass # Write out a formatted spoiler log

spoilers = {}
for r, room in rooms.items():
    for n, setup in room.setups.items():
        for actor in setup['actors']:
            if not isEnemyActor(actor.filename):
                continue
            i = available_actors.index(actor.filename)
            actor.setObject(available_objects[i])
        setup_spoiler = {'objects':[],'actors':[]}
        _getRoomName = lambda r,n: '{}-{} ({})'.format(r,n,room.descr)
#         print('{}-{}'.format(r,n))
        spoilers[_getRoomName(r,n)] = setup_spoiler
        possible_objects = []
        for obj in setup['objects']:
            if not isEnemyObject(obj.filename):
                continue
            tpe = _getObjType(obj, setup['actors'], (r,n)) # Function will need to look at the related actor to see what the type is
            if not tpe:
                continue
            new_obj = random.choice(_getObjs(tpe)) if not selected_enemy else selected_enemy['object_fn']
            room.replaceObject(obj.filename, new_obj, n)
            possible_objects.append(new_obj)
            setup_spoiler['objects'].append({'old':obj.filename, 'new':new_obj})
        for actor in setup['actors']:
            # I have to figure out a way to find the index
        
            index = [i for i in setup['actors'] if i.filename == actor.filename].index(actor)
            
            var_str = '{}-{}'.format(actor.filename,actor.var)
            if not (isEnemyActor(actor.filename) and var_str in list(actor_var_pairs.keys())+list(from_actor_var_pairs.keys())) :
                if isEnemyActor(actor.filename):
#                     if room.fn == 'Bmori1_room_6':
#                         raise Exception()
                        

                    pass#print("Excluding {}/{} in room {} setup # {}".format(actor.filename, actor.var, room.fn, n))
                continue # Only randomize enemies that have defined variables 

            choices = _getAvailableActors(actor, possible_objects)
            if len(choices) == 0:
                continue # This should account for cases where 1 actor in a room can't be randomized but other's can
                # Because otherwise the object would get changed out and then the one that didn't get randomized won't spawn

            choice = random.choice(choices)# ( actor, var_list)
            new_actor = choice[0] if not selected_enemy else selected_enemy['fn']
            new_var = random.choice(choice[1]) if not selected_enemy else selected_enemy['var'] # (varid, descr)
            setup_spoiler['actors'].append({'old': actor.filename, 'new': new_actor, 'old_var': actor.var, 'new_var': new_var, 'descr': new_actor[2]})
            room.replaceActor(actor.filename, new_actor, new_var=new_var[0], index=index, setup=n, replaceObject=False)
print("Rooms Randomized, {} sec".format(time.time()-start_time))

# Optionally set the spawn location
accessor.spawnAt(0x3)

# Print out spoilers
_writeEnemySpoilers(spoilers, "spoiler.log")
print("Replacement Log Written".format(time.time()-start_time))

accessor.writeData()
print("New ROM Written {}".format(time.time()-start_time))