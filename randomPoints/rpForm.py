from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

class dialogForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Random Points")

        #choose from list or canvas
        comboLayout=QHBoxLayout() #1

        comboLabel=QLabel("Active &layers") #A
        self.chooseCombo=QComboBox()
        comboLabel.setBuddy(self.chooseCombo)
        comboLayout.addWidget(comboLabel)
        comboLayout.addWidget(self.chooseCombo)

        comboLayout.addStretch()

        checkLabel=QLabel("Active &window") #B
        self.checkCanvas=QCheckBox()
        checkLabel.setBuddy(self.checkCanvas)
        comboLayout.addWidget(self.checkCanvas)
        comboLayout.addWidget(checkLabel)

        #choose from disc 
        fieldLayout=QHBoxLayout() #2
        fieldLabel=QLabel("&File from disc")
        self.chooseField=QLineEdit()
        chooseFiledButton=QPushButton("...")
        fieldLabel.setBuddy(self.chooseField)
        fieldLayout.addWidget(fieldLabel)
        fieldLayout.addWidget(self.chooseField)
        fieldLayout.addWidget(chooseFiledButton)

        #points and buffer 
        setupLayout=QHBoxLayout()  #3

        self.npointsSpin=QSpinBox() #A
        self.npointsSpin.setMinimum(1)
        npointsLabel=QLabel("Number of &points")
        npointsLabel.setBuddy(self.npointsSpin)
        setupLayout.addWidget(npointsLabel)
        setupLayout.addWidget(self.npointsSpin)

        self.bufferField=QLineEdit() #B
        bufferLabel=QLabel("Size of &Buffer")
        bufferLabel.setBuddy(self.bufferField)
        self.bufferField.setText("0")
        setupLayout.addWidget(bufferLabel)
        setupLayout.addWidget(self.bufferField)
        setupLayout.addStretch()

        #standard buttons 
        buttonBox = QDialogButtonBox() #4
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        #final layout
        mainLayout=QVBoxLayout() #5
        mainLayout.addLayout(comboLayout)
        mainLayout.addLayout(fieldLayout)
        mainLayout.addLayout(setupLayout)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        #basic connections
        buttonBox.accepted.connect(self.accept) #4
        buttonBox.rejected.connect(self.reject)
        chooseFiledButton.clicked.connect(self.chooseButton_clicked) #2A
        self.chooseCombo.currentIndexChanged.connect(lambda: self.change("combo")) #6B
        self.checkCanvas.stateChanged.connect(lambda: self.change("check"))

    def chooseButton_clicked(self): #2A
        fileName = QFileDialog.\
            getOpenFileName(self,"File to take extend from", "","All Files (*)") #2B
        self.chooseField.setText(fileName) #2C
        # remove remained selectors
        self.change("field") #6A

    def change(self,what): #6
      ''' This function allow to reset other elements 
          except pointed by `what` var '''
      if what != "combo": self.chooseCombo.setCurrentIndex(0)
      if what != "check": self.checkCanvas.setChecked(False)
      if what != "field": self.chooseField.clear()

