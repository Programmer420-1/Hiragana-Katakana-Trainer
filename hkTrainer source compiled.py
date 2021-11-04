import sys
import os
import time
import random
import winsound
import threading
import json
import ctypes
from PyQt5.uic.uiparser import QtCore
import pyautogui
from datetime import date
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QSize, QVariantAnimation, QAbstractAnimation
from PyQt5.QtGui import QColor, QIcon
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QLabel, QMainWindow, QPushButton, QStackedWidget, QWidget, QDesktopWidget,QMessageBox

# const kana and gana sets
GANA_dict = {}
KANA_dict = {}

# mutable kana or gana sets
practice_dict = {}

# scoring var
score  = 0
totalAttempts = 0
totalCorrect = 0
pointer = 0

# initial states
kanaMode = False
ganaMode = False
sound = True
timeStart = 0
timeEnd = 0
status = 0


# paths
path = os.getcwd()
mutepng = path + r"\Resources\graphics\mute.png"
unmutepng = path + r"\Resources\graphics\unmute.png"
quitpng = path + r"\Resources\graphics\quit.png"
correctSFX = path + r"\Sound effect\Correct sound effect.wav"
wrongSFX = path + r"\Sound effect\wrong sound effect.wav"
enterpng = path + r"\Resources\graphics\enter.png"
indexui = path + r"\Resources\ui files\index.ui"
mainui = path + r"\Resources\ui files\main.ui"
endui = path + r"\Resources\ui files\end.ui"
syllabary = path + r"\Syllabary\Japanese Syllabary.json"

def loadJson(filePath):
    global GANA_dict,KANA_dict
    with open(filePath,"r") as f:
        japaneseSyb = json.load(f)
        if japaneseSyb["language"] != "Japanese":
            return 0
        else:
            GANA_dict = japaneseSyb["content"][0]["sets"]
            KANA_dict = japaneseSyb["content"][1]["sets"]
            return 1

def getKey(value,dict):
    # get list of keys
    keys = dict.keys()
    for key in keys:
        try:
            if value == dict[key]:
                # In case of duplicated values, delete the found keys in ori dict before proceeding
                del dict[key]
                return key
        except Exception as e:
            # for debugging purpose
            print(e)

class indexWindow(QMainWindow):
    def __init__(self):
        super(indexWindow, self).__init__()
        loadUi(indexui,self)
        self.warning.hide()
        self.setWindowTitle("Hiragana and Katagana Trainer")
        self.startButton.clicked.connect(self.startMain)

    def startMain(self):
        global kanaMode,ganaMode
        kanaMode = self.Katakana.isChecked()
        ganaMode = self.Hiragana.isChecked()

        if kanaMode == False and ganaMode == False:
            self.warning.show()
        else:
            global practice_dict
            if kanaMode == True and ganaMode == False:
                practice_dict = dict(self.dictRandomizer(KANA_dict))
            elif kanaMode == False and ganaMode == True:
                practice_dict = dict(self.dictRandomizer(GANA_dict))
            else:
                practice_dict = dict(self.dictRandomizer(GANA_dict,KANA_dict))
            main = mainWindow()
            widget.addWidget(main)
            widget.setCurrentIndex(widget.currentIndex() +1)
    
    def dictRandomizer(self,dict1,dict2 = {}):
        dict3 = {**dict1, **dict2}
        length = len(dict3.keys())
        
        indexes = []
        for i in range(length):
            indexes.append(i)
        random.seed()
        random.shuffle(indexes)
        #print(indexes)

        keys = list(dict3.keys())
        
        randomDict = {}
        for i in indexes:
            randomDict[str(keys[i])] = dict3[keys[i]]
        
        return randomDict

class mainWindow(QMainWindow):
    def __init__(self):
        global kanaMode,ganaMode,practice_dict,totalAttempts,totalCorrect,score,pointer,sound
        super(mainWindow,self).__init__()
        loadUi(mainui,self)
        MODE = self.getMode(kanaMode,ganaMode)
        questions = list(practice_dict.keys())
        self.question.setText(f"{questions[pointer]}")
        self.mode.setText(f"Current mode : {MODE}")
        self.totalAttempts.setText(f"Total Attempts : {str(totalAttempts)}")
        self.totalUnattempts.setText(f"Questions Left : {str(len(practice_dict.keys())-1)}")
        self.score.setText(f"Current Score : {str(score)}%")
        self.progressBar.setMaximum(len(questions)-1)
        self.progressBar.setValue(0)
        self.submit.setIcon(QIcon(enterpng))
        self.submit.setIconSize(QSize(99,36))
        self.stopButton.setIcon(QIcon(quitpng))
        self.stopButton.setIconSize(QSize(35,35))
        
        if sound == True:
            self.soundButton.setIcon(QIcon(unmutepng))
            self.soundButton.setIconSize(QSize(50,50))
        else:
            self.soundButton.setIcon(QIcon(mutepng))
            self.soundButton.setIconSize(QSize(40,40))

        self.submit.clicked.connect(self.validateAnswer)
        self.soundButton.clicked.connect(self.playSound)
        self.stopButton.clicked.connect(self.quit)
    
    def getMode(self,kanaMode,ganaMode):
        if kanaMode == True and ganaMode == False:
            MODE = "Katakana only"
        elif kanaMode == False and ganaMode == True:
            MODE = "Hiragana only"
        else:
            MODE = "Gana and Kana"
        return MODE
    
    def scoreCounter(self,totalCorrect,totalAttempts):
        try:
            score = '{:.2f}'.format((totalCorrect/totalAttempts)*100)
            return score
        except:
            return 0
        
    def validateAnswer(self):
        global totalAttempts,totalCorrect,pointer,practice_dict,sound,score
        questions = list(practice_dict.keys())
        answer = self.answerBox.text()

        if pointer+1 == len(questions):
            end = endWindow()
            widget.addWidget(end)
            widget.setCurrentIndex(widget.currentIndex()+1)
        
        else:
            if answer in practice_dict[questions[pointer]].split(","):
                if sound == True:
                    t = threading.Thread(target = lambda:winsound.PlaySound(correctSFX,winsound.SND_FILENAME), daemon=True)
                    t.start()
                totalAttempts += 1
                totalCorrect += 1
                pointer += 1
                self.totalUnattempts.setText(f"Questions Left : {str(len(practice_dict.keys())-1-pointer)}")
                self.question.setText(f"{questions[pointer]}")
                self.progressBar.setValue(totalCorrect)
                #print(pointer)
            
            else:
                if sound == True:
                    t = threading.Thread(target = lambda:winsound.PlaySound(wrongSFX,winsound.SND_FILENAME), daemon=True)
                    t.start()
                totalAttempts += 1

            score = self.scoreCounter(totalCorrect,totalAttempts)
            self.totalAttempts.setText(f"Total Attempts : {str(totalAttempts)}")
            self.score.setText(f"Current Score : {str(score)}%")
            self.answerBox.clear()
            self.answerBox.setFocus()

    def playSound(self):
        global sound 
        if sound == True:
            sound = False
            self.soundButton.setIcon(QIcon(mutepng))
            self.soundButton.setIconSize(QSize(40,40))
        else:
            sound = True
            self.soundButton.setIcon(QIcon(unmutepng))
            self.soundButton.setIconSize(QSize(50,50))

    def quit(self):
        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setText("Are you sure you want to give up now?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        returnVal = msg.exec()

        if returnVal == QMessageBox.Yes:
            end = endWindow()
            widget.addWidget(end)
            widget.setCurrentIndex(widget.currentIndex()+1)
        else:
            pass

class endWindow(QMainWindow):
    def __init__(self):
        global score
        super(endWindow,self).__init__()
        loadUi(endui,self)
        self.finalScore.setText(f"{score}%")
        self.againButton.clicked.connect(self.reset)
        self.quitButton.clicked.connect(self.quit)

    def reset(self):
        global score,totalCorrect,totalAttempts,practice_dict,pointer,kanaMode,ganaMode
        score,totalCorrect,totalAttempts,pointer = 0,0,0,0
        practice_dict.clear()
        kanaMode = False
        ganaMode = False

        index = indexWindow()
        widget.addWidget(index)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def quit(self):
        global score,totalCorrect,totalAttempts,practice_dict,pointer
        score,totalCorrect,totalAttempts,pointer = 0,0,0,0
        practice_dict.clear()
        
        pyautogui.hotkey("alt","f4")


#main 
os.chdir(path)
app = QApplication(sys.argv)
try: 
    loadJson(syllabary)
    status = 1
except:
    popup = QMessageBox()
    popup.setWindowTitle("Read Error")
    popup.setText("Syllabary file do not exists")
    popup.setStyleSheet("QLabel{height: 75px; min-height: 75px; max-height: 75px;}")
    popup.setIcon(QMessageBox.Critical)
    popup.addButton(QPushButton("Quit"),QMessageBox.NoRole)
    popup.addButton(QPushButton("Browse File"),QMessageBox.YesRole)
    action = popup.exec_()

    if action==1:
        dialog = QFileDialog()
        fileName = dialog.getOpenFileName(None,'Open File',"C:\Program Files")
        filePath = fileName[0]
        try:
            status = loadJson(filePath)
        except:
            statux = 0

        if status == 0:
            errorPop = QMessageBox()
            errorPop.setWindowTitle("Read Error")
            errorPop.setText("Error occured while reading")
            errorPop.setInformativeText("Please make sure that selected the correct file. Press Ok to exit")
            errorPop.setStyleSheet("QLabel{height: 50px; min-height: 50px; max-height: 50px;}")
            errorPop.setIcon(QMessageBox.Critical)
            errorPop.addButton(QPushButton("Ok"),QMessageBox.YesRole)
            action = errorPop.exec_()
            if action == 0:
                app.quit()
    else:
        app.quit()

if status == 1:
    welcome = indexWindow()
    widget = QStackedWidget()
    widget.addWidget(welcome)
    widget.setFixedHeight(720)
    widget.setFixedWidth(1280)
    widget.show()
    try:
        sys.exit(app.exec())
    except:
        pass

