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
    def read(self):
        raise NotImplementedError("Must be implemented in subclass")
    def lookupObjectDescription(self, fn):
        raise NotImplementedError("Must be implemented in subclass")
    def lookupObjectNum(self, fn):
        raise NotImplementedError("Must be implemented in subclass")
    def lookupActorNum(self, fn):
        raise NotImplementedError("Must be implemented in subclass")
    def getRoomAddrByName(self, name):
        raise NotImplementedError("Must be implemented in subclass")
    def getRoomNames(self):
        raise NotImplementedError("Must be implemented in subclass")
    def getObjectNames(self):
        raise NotImplementedError("Must be implemented in subclass")
    def lookupObjectByIndex(self, index):
        raise NotImplementedError("Must be implemented in subclass")
    def lookupObjectFieldByIndex(self, index, fieldname):
        raise NotImplementedError("Must be implemented in subclass")
    def lookupActorByIndex(self, index):
        raise NotImplementedError("Must be implemented in subclass")
    def lookupActorFieldByIndex(self, index, fieldname):
        raise NotImplementedError("Must be implemented in subclass")

class PandasDataReader(DataReader):
    def __init__(self, fn='data.xlsx', update=False):
        DataReader.__init__(self, fn, update)
    def read(self):
        if self.fn.endswith('.xlsx'):
            return self._readXLSX()
    def _readXLSX(self):
        import xlrd
        import pandas as pd
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
        x = self.refobjects[self.ref.objects['Filename'] == fn].index[0] # Get the record No
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
    def lookupObjectByIndex(self, index):
        return self.ref.objects.loc[index]
    def lookupObjectFieldByIndex(self, index, fieldname):
        return self.ref.objects.loc[index][fieldname]
    def lookupActorByIndex(self, index):
        return self.ref.actors.loc[index]
    def lookupActorFieldByIndex(self, index, fieldname):
        return self.ref.actors.loc[index][fieldname]