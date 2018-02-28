# Austin Hasten
# Initial commit - February 28th, 2018

import os
import urllib.request
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from itertools import chain
from .dummyimporting import ImportDialog

class IMDbToAnki(QDialog):
    def __init__(self):
        super().__init__()
        try:
            from imdbpie import Imdb
        except ImportError:
            showInfo('Please install the imdbpie module.')
            return
        self.imdb = Imdb()
        self.mainLayout = QGridLayout(self)
        self.queryInput = QLineEdit()
        self.searchResults = QListWidget()
        self.createButton = QPushButton("Create")
        self.createButton.setAutoDefault(False)
        self.sidebar = QWidget()
        self.sidebarLayout = QVBoxLayout(self.sidebar)
        # All valid tokens for imdbpie Person objects.
        self.departments = [
                'director', 'writer', 'cast', 'producer', 'cinematographer', 'editor',
                'casting_director', 'production_designer', 'art_director', 'set_decorator',
                'costume_designer', 'make_up_department', 'assistant_director',
                'art_department', 'sound_department', 'visual_effects',
                'music_department', 'miscellaneous' ]
        self.depBoxes = [ QCheckBox(token) for token in self.departments ]
        for box in self.depBoxes:
            self.sidebarLayout.addWidget(box)
        self.queryInput.returnPressed.connect(self.search)
        self.createButton.clicked.connect(self.createNotes)
        self.mainLayout.addWidget(self.queryInput, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.searchResults, 1, 0, 1, 1)
        self.mainLayout.addWidget(self.createButton, 2, 0, 1, 1)
        self.mainLayout.addWidget(self.sidebar, 0, 1, 3, 1)
        self.exec_()

    def search(self):
        self.searchResults.clear()
        for result in self.imdb.search_for_title(self.queryInput.text()):
            item = QListWidgetItem(f'{result["title"]} ({result["year"]})', self.searchResults)
            item.setData(Qt.UserRole, result['imdb_id'])
        self.searchResults.setCurrentRow(0)

    def credits(self):
        title = self.searchResults.currentItem().data(Qt.UserRole)
        departments = self.imdb.get_title_credits(title)['credits']
        enabledDeps = [ box.text() for box in self.depBoxes if box.checkState() ]
        return list(chain.from_iterable([ departments[dep] for dep in enabledDeps ]))

    def createNotes(self):
        mw.progress.start(immediate=True)
        titleYear = self.searchResults.currentItem().text()
        data = [ ';'.join([titleYear, Person(p).fields]) for p in self.credits() ]
        mw.progress.finish()
        ImportDialog(mw, ['Film Title', 'Name', 'Role', 'Image', 'Tags'], data)

class Person():
    def __init__(self, person):
        self.name = person['name']
        self.role = ', '.join([ role['character'] for role in person.get('roles', [])])
        self.job = person.get('job')
        self.data = next(filter(None, iter([self.role, self.job])), person['category'])
        self.imgURL = person.get('image', {}).get('url')
        self.imgHTML = f'<img src="{self.name}.jpg">'
        self.tags = ' '.join(['imdbtoanki'] + person.get('attr', []))
        self.fields = ';'.join([self.name, self.data, self.imgHTML, self.tags])
        if self.imgURL:
            path = os.path.join(mw.col.media.dir(), f'{self.name}.jpg')
            urllib.request.urlretrieve(self.imgURL, path, self.reporthook)

    def reporthook(self, *args):
        mw.app.processEvents()

def start():
    mw.myWidget = widget = IMDbToAnki()

action = QAction('IMDbToAnki')
action.triggered.connect(start)
mw.form.menuTools.addAction(action)
