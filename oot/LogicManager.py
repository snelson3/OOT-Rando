import random
class LogicManager:
    def __init__(self, accessor):
        self.accessor = accessor
    def makeAssumption(self, check, msg):
        if not check:
            if self.accessor.forceAssumptions:
                raise Exception("ERROR: {}".format(msg))
            print("WARNING: {}")
    def canRandomizeObject(self, obj, actors):
        # The issue is the lookupEnemy function call
        #  it's checking for the existence of an actor with proper vars but I don't think it should be doing that
        #  as it invalidates the canRandomize* methods
        #  but some enemies can be different based on vars
        # maybe the key is having lookupEnemy return all the enemies that can match
        if not self.accessor.reader.isEnemy(object_name=obj.filename):
            return False
        # Find all matching actors
        poss = [a for a in actors if a.object_name == obj.filename]
        # Find requirements of all actors
        if len(poss) == 0:
            return False # the actor is not explicitly defined, probably dynamically generated
        numReqs = len(set([self.accessor.lookupEnemy(p)["type"] for p in poss]))
        self.makeAssumption(numReqs == 1, "Object in a room has actors with multiple requirements")
        def _hasGoodVars(a):
            enemy = self.accessor.lookupEnemy(a)
            return a.var in [v.var for v in enemy["variables"] + enemy["from_variables"]]
        # filter to actors with variables in the enemies randomize list
        good = [p for p in poss if _hasGoodVars(p)]
        if len(good) == 0:
            return False
        self.makeAssumption(len(good)==len(poss), "Some actors in room can be randomized, others can't")
        return True
    def getNewObject(self, obj, actors):
        # Find all matching actors
        def _getObjsOfType(t):
            return [e for e in self.accessor.enemies if e["type"] == t]
        poss = [a for a in actors if a.object_name == obj.filename]
        tpe = self.accessor.lookupEnemy(poss[0])["type"]
        choice = random.choice(_getObjsOfType(tpe)) if not self.accessor.selected_enemy else self.accessor.selected_enemy
        return choice["object_fn"]
    def canRandomizeActor(self, actor):
        if not self.accessor.reader.isEnemy(actor_name=actor.filename):
            return False
        poss_enemies = [e for e in self.accessor.enemies if e["actor_fn"] == actor.filename]
        for enemy in poss_enemies:
            if actor.var in [v.var for v in enemy["variables"] + enemy["from_variables"]]:
                return True
        return False
    def getNewActor(self, actor, objects):
        curr_enemy = self.accessor.lookupEnemy(actor)
        tpe = curr_enemy["type"]
        possible_enemies = [e for e in self.accessor.enemies if e["type"] == tpe and e["object_fn"] in [o.filename for o in objects]]
        new_enemy = random.choice(possible_enemies) if not self.accessor.selected_enemy else self.accessor.selected_enemy["actor_fn"]
        # TODO Selected enemy is broken here, because the selected var is not an namedtuple (and new enemy is bad)
        var = random.choice(new_enemy["variables"]) if not self.accessor.selected_enemy else self.accessor.selected_enemy["var"]
        return new_enemy["actor_fn"], var