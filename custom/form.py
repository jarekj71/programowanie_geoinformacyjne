from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class message(QDialog):
    def __init__(self):
        super().__init__() #1
        self.resize(300,100) #1
        self.setWindowTitle("Plugin?") #1
        self.infoLabel = QLabel("Tak, to jest plugin!") #2
        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel|QDialogButtonBox.Ok) #3
        mainLayout=QVBoxLayout() #4 
        mainLayout.addWidget(self.infoLabel) #5
        mainLayout.addStretch() #6
        mainLayout.addWidget(buttonBox) #7
        self.setLayout(mainLayout) #8
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
