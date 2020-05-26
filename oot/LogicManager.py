import random, os
class LogicManager:
    def __init__(self, accessor):
        self.accessor = accessor
        self.logdir = "logs"
    def _getSet(self, l):
        return set([str(i) for i in l])
    def writeEnemySpoilers(self, spoilers, fn):
        fn = os.path.join(self.logdir, fn)
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
                    f.write('  {} [{}] -> {} [{}]\n'.format(a['old'], a['old_var'], a['new'], a['new_var']))
    def makeAssumption(self, check, err):
        if not check:
            if self.accessor.forceAssumptions:
                raise Exception("ERROR: {}".format(err))
            print("WARNING: {}")
    def canRandomizeObject(self, obj, actors):
        if not self.accessor.reader.isEnemy(object_name=obj.filename):
            return False
        def _lookupEnemy(en):
            options = self.accessor.lookupEnemy(en)
            if len(options) == 0:
                return None
            for option in options:
                if en.var in [v.var for v in option["variables"] + option["from_variables"]]:
                    return option
            return None # Enemy didn't have matching var
        # Find all matching actors
        poss = [_lookupEnemy(a) for a in actors if a.object_name == obj.filename]
        # Find requirements of all actors
        if len(poss) == 0:
            return False # the actor is not explicitly defined, probably dynamically generated
        if None in poss:
            # Possible some actors could be randomized while others can't but just deferring to False for now
            return False
        numReqs = len(self._getSet([p["type"] for p in poss]))
        if numReqs > 1:
            return False # At least 1 room in spirit has invisible floormaster + a visible wallmaster
        return True
    def getNewObject(self, obj, actors):
        # Find all matching actors
        def _getObjsOfType(t):
            return [e for e in self.accessor.enemies if e["type"] == t]
        def _lookupEnemy(en):
            options = self.accessor.lookupEnemy(en)
            for option in options:
                if en.var in [v.var for v in option["variables"] + option["from_variables"]]:
                    return option
            raise Exception("Enemy that is allowed to be randomized has no matching variable")
        poss = [a for a in actors if a.object_name == obj.filename]
        tpe = _lookupEnemy(poss[0])["type"]
        choice = random.choice(_getObjsOfType(tpe)) if not self.accessor.selected_enemy else self.accessor.selected_enemy
        return choice["object_fn"]
    def canRandomizeActor(self, actor, randomizable_objects):
        if not self.accessor.reader.isEnemy(actor_name=actor.filename):
            return False
        # Checking this is kind of a hack and is excessive, but larger refactor later will eliminate this
        if not actor.object_name in [o.filename for o in randomizable_objects]:
            return False
        poss_enemies = [e for e in self.accessor.enemies if e["actor_fn"] == actor.filename]
        for enemy in poss_enemies:
            if actor.var in [v.var for v in enemy["variables"] + enemy["from_variables"]]:
                return True
        return False
    def getNewActor(self, actor, objects):
        def _lookupEnemy(en):
            options = self.accessor.lookupEnemy(en)
            for option in options:
                if en.var in [v.var for v in option["variables"] + option["from_variables"]]:
                    return option
            raise Exception("Enemy that is allowed to be randomized has no matching variable")
        curr_enemy = _lookupEnemy(actor)
        tpe = curr_enemy["type"]
        # Paring down all the available enemies to the ones with an objectfn in objects and whose type match
        possible_enemies = [e for e in self.accessor.enemies if e["type"] == tpe and e["object_fn"] in objects]
        new_enemy = random.choice(possible_enemies) if not self.accessor.selected_enemy else self.accessor.selected_enemy["actor_fn"]
        # TODO Selected enemy is broken here, because the selected var is not an namedtuple (and new enemy is bad)
        var = random.choice(new_enemy["variables"]) if not self.accessor.selected_enemy else self.accessor.selected_enemy["var"]
        return new_enemy["actor_fn"], var