from collections import namedtuple
import os
from .Utils import *


class DataReader:
    def __init__(self, fn='data.xlsx', update=False):
        self.fn = fn
        if update or not os.path.isfile(self.fn):
            self.updateDataFile()
        self.ref = self.read()
    def updateDataFile():
        req = requests.get('https://drive.google.com/uc?authuser=0&id=1kjLzvYSLfFtsRoVEtSMwpmZEcwCSEJIX&export=download')
        with open(fn, "wb") as f:
            f.write(req.content)
    def _notImplemented():
        raise NotImplementedError("Must be implemented in subclass")
    def read(self):
        self._notImplemented()
    def lookupObjectDescription(self, fn):
        self._notImplemented()
    def lookupObjectNum(self, fn):
        self._notImplemented()
    def lookupActorNum(self, fn):
        self._notImplemented()
    def getRoomAddrByName(self, name):
        self._notImplemented()
    def getRoomNames(self):
        self._notImplemented()
    def getObjectNames(self):
        self._notImplemented()
    def lookupObjectByIndex(self, index):
        self._notImplemented()
    def lookupObjectFieldByIndex(self, index, fieldname):
        self._notImplemented()
    def lookupActorByIndex(self, index):
        self._notImplemented()
    def lookupActorFieldByIndex(self, index, fieldname):
        self._notImplemented()
    def lookupEnemyIndex(self):
        self._notImplemented()
    def lookupEnemyByIndex(self, index):
        self._notImplemented()
    def getEnemyActorNames(self):
        self._notImplemented()
    def getEnemyObjectNames(self):
        self._notImplemented()
    def isEnemy(self, object_name=False, actor_name=False):
        self._notImplemented()
    def lookupEnemies(self, key, value):
        self._notImplemented()
    def listEnemies(self):
        self._notImplemented()

import xlrd
import pandas as pd

class PandasDataReader(DataReader):
    def __init__(self, fn='data.xlsx', update=False):
        DataReader.__init__(self, fn, update)
    def read(self):
        if self.fn.endswith('.xlsx'):
            return self._readXLSX()
    def _readXLSX(self):
        book = xlrd.open_workbook(self.fn)
        def _sheetToPandas(name):
            sheet = book.sheet_by_name(name)
            table = [[c.value for c in r] for r in sheet.get_rows()]
            table_headers = table[0]
            table_data = table[1:]
            return pd.DataFrame(table_data, columns=table_headers)
        Reference = namedtuple('Reference', 'files actors objects enemies')
        return Reference(
                files=_sheetToPandas('files').set_index('Filename'),
                actors=_sheetToPandas('actors').set_index('Record No'),
                objects=_sheetToPandas('objects').set_index('Record No'),
                enemies=_sheetToPandas('enemies').set_index('Enemy')
                )
    def _lookupRef(self, ref, key, filterValue=None):
        f = ref.set_index(key)
        if filterValue:
            f = f.loc[filterValue]
        if len(f) == 0:
            return []
        if hasattr(f, "pivot_table"): # more than one result is a dataframe
            return f.reset_index().to_dict(orient="records")
        name = f.name
        f = f.to_dict()
        f[key] = name
        return [f]
    def lookupObjectDescription(self, fn):
        x = self.ref.objects[self.ref.objects['Filename'] == fn]['Description'][0]
        # I think this is necessary
        if type(x) == pd.core.series.Series:
            x = x.iloc[0] # There's only two object duplicates
        return x
    def lookupObjectNum(self, fn):
        x = self.ref.objects[self.ref.objects['Filename'] == fn].index[0] # Get the record No
        if type(x) == pd.core.series.Series:
            x = x.iloc[0] # There's only two object duplicates
        return x
    def lookupActorNum(self, fn):
        return self.ref.actors[self.ref.actors['Filename'] == fn].index[0] # Get the record No
    def getRoomAddrByName(self, name):
        record = self.ref.files.loc[name]
        return record['VROM Start']
    def getRoomNames(self):
        df_filenames = self.ref.files[self.ref.files['Description'] == 'Scenes/Rooms'].index
        return [r for r in df_filenames if "_room_" in r]  # We don't want the scenes
    def getObjectNames(self):
        return self.ref.objects.index
    def getEnemyIndex(self):
        return self.ref.enemies.index
    def getEnemyActorNames(self):
        return list(self.ref.enemies['Actor FN'].values)
    def getEnemyObjectNames(self):
        return list(self.ref.enemies['Object FN'].values)
    def lookupEnemyByIndex(self, index):
        return self.ref.enemies.loc[index]
    def lookupObjectByIndex(self, index):
        return self.ref.objects.loc[index]
    def lookupObjectFieldByIndex(self, index, fieldname):
        return self.ref.objects.loc[index][fieldname]
    def lookupActorByIndex(self, index):
        return self.ref.actors.loc[index]
    def lookupActorFieldByIndex(self, index, fieldname):
        return self.ref.actors.loc[index][fieldname]
    def lookupEnemyByName(self, object_name=False, actor_name=False):
        # If two or more rows match, it only returns the first
        if not self.isEnemy(object_name, actor_name):
            raise Exception("Provided name does not belong to an enemy")
        if object_name:
            enemies = self.lookupEnemies("Object FN", object_name)
        else:
            enemies = self.lookupEnemies("Actor FN", actor_name)
        if len(enemies) == 0:
            raise Exception("Can't find enemy")
        return enemies[0]
    def lookupEnemyFieldByName(self, fieldname, object_name=False, actor_name=False):
        return self.lookupEnemyByName(object_name, actor_name)[fieldname]
    def isEnemy(self, object_name=False, actor_name=False):
        if (not (object_name or actor_name)) or (object_name and actor_name):
            raise Exception("Exactly one of 'object_name' or 'actor_name' must be defined")
        if object_name:
            return object_name in self.getEnemyObjectNames()
        return actor_name in self.getEnemyActorNames()
    def lookupEnemies(self, key="Enemy", value=None):
        return self._lookupRef(self.ref.enemies.reset_index(), key, value)
    def listEnemies(self):
        enemies = []
        for enemy in self.getEnemyIndex():
            enemy_info = self.lookupEnemyByIndex(enemy)
            if enemy_info['Enabled']:
                enemies.append({
                    "actor_fn": enemy_info["Actor FN"],
                    "object_fn": enemy_info["Object FN"],
                    "variables": parseVariableList(enemy_info["Variables"]),
                    "from_variables": parseVariableList(enemy_info["From-Vars"]),
                    "type": enemy_info["Requirements"],
                    "name": enemy
                })
        return enemies