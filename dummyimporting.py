# Austin Hasten
# Initial Commit - February 28th, 2018

from aqt.importing import ImportDialog
from anki.importing.csvfile import TextImporter

class DummyImporter(TextImporter):
    def __init__(self, flds, data, col):
        super().__init__(col, None)
        self.flds = flds
        self.data = data
        self.numFields = len(self.flds)
        self.delimiter = ';'
        self.dialect = None
        self.fileobj = open('dummy', 'w+')

class ImportDialog(ImportDialog):
    def __init__(self, mw, flds, data):
        super().__init__(mw, DummyImporter(flds, data, mw.col))

    def exec_(self):
        self.frm.importMode.setCurrentIndex(2)
        self.frm.importMode.close()
        self.frm.allowHTML.close()
        self.frm.autoDetect.close()
        super().exec_()

    def showMapping(self, keepMapping=False, hook=None):
        super().showMapping(keepMapping, hook)
        for num in range(len(self.mapping)):
            text = f"<b>{self.importer.flds[num]}</b> is:"
            self.grid.itemAtPosition(num, 0).widget().setText(text)
