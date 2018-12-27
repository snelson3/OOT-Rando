from collections import namedtuple
import os



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

#TODO Break into own file
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