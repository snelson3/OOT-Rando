# This class provides useful accessor methods for figuring out information from the enemies section of the data

class EnemyMapper():
    def __init__(self, reader):
        self.reader = reader
        self.filterDisabled = True
    def listEnemies(self, requirements=None):
        enemies = self.reader.lookupEnemies(key="Requirements")
        if self.filterDisabled:
            enemies = list(filter(lambda k: k["enabled"], enemies))
        return enemies
    def getEnemy(self, requirements=None, actor_name=None, object_name=None):
        # May need caching if it slows things down
        enemies = self.listEnemies(requirements=requirements)
        if actor_name:
            enemies = [e for e in enemies if e["Actor FN"] == actor_name]
        if object_name:
            enemies = [e for e in emeies if e["Object FN"] == object_name]
        if len(enemies) == 0:
            return None
        if len(enemies) > 1:
            raise Exception("Found too many enemy records\n\n{}".format(enemies))
    def listActorVariables(self, actor, fromVars="No"):
        # This needs to do more because the variables are of the form x () y ()
        removeBlanks = lambda l: list(filter(lambda i: len(i) > 1, l))
        if fromVars == "No":
            return removeBlanks(actor["Variable's"].split(",")) # this liine might be unfinished
        if fromVars == "Both":
            return removeBlanks(actor["Variable's"].split(",")+actor["From-Var's"].split(","))
        if fromVars == "Yes":
            return removeBlanks(actor["From-Var's"].split(","))
        raise Exception("Unexpected fromVars value: {}".format(fromVars))
    def lookupActorVar(self, actor, var, requirements):
        enemy = self.getEnemy(requirements=requirements, actor_name=actor)
        # Might need a selectedVar thing, but going to try not storing it
        return enemy
