from ping3 import ping
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QFont,QIcon,QPainter,QPen,QPalette,QColor
from PyQt5 import uic,QtCore
import sys
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup as bs
from time import sleep

class WorldFetcher(QtCore.QThread):
    worldSignal = QtCore.pyqtSignal(list)
    worldParsedSignal = QtCore.pyqtSignal(int)
    worldTotalSignal = QtCore.pyqtSignal(int)
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()


    def run(self):
        worlds = self.getWorlds()
        self.worldSignal.emit(worlds)
    
    def getWorlds(self):
        html = requests.get("http://oldschool.runescape.com/slu").text

        soup = bs(html,"html.parser")

        worldWrapper = soup.find_all(attrs={"class":"server-list__body"})[0]
        worlds = worldWrapper.findChildren("tr")


        parsedWorlds = []
        totalWorlds = len(worlds)
        self.worldTotalSignal.emit(totalWorlds)
        for worldCount,world in enumerate(worlds,1):
            membersWorld = False
            classNames = world.get("class")
            #for className in classNames:
            #    flags = className.split("--")[1:]
            #    if len(flags) != 0:
            #        print(flags)
            #    if "members" in flags:
            #        membersWorld = True

            worldChildren = list(filter(lambda i: i != "\n",list(world.children)))
            
            worldInfo = worldChildren[0]
            players = worldChildren[1].string
            if players == None:
                players = "Full"
            else:
                players = players.split()[0]
            country = worldChildren[2].string
            worldType = worldChildren[3].string
            worldActivity = worldChildren[4].string

            if worldActivity == "-":
                worldActivity = ""

            worldNumber = worldInfo.find("a")["id"].split("-")[-1]
        
            parsedWorlds.append({"world":worldNumber,"players":players,"country":country,"worldType":worldType,"worldActivity":worldActivity})
            self.worldParsedSignal.emit(worldCount)
        return parsedWorlds


def getServerPing(world):
    return ping(f"oldschool{world}.runescape.com")


def addStyle(obj,style):
    obj.setStyleSheet(obj.styleSheet()+makeCSS(style))


def updateStyle(obj):
    obj.style().unpolish(obj)
    obj.style().polish(obj)
    obj.update()

def makeCSS(css):
    cssString = ""
    for key in css.keys():
        value = css[key]
        if value[-1] != ";":
            value+=";"
        cssString+=key+":"+value
    return cssString



class QHLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("border:none;border-top:1px solid gray;")

class Console(QScrollArea):
    ERRORSTYLE = [{"color":"red"},{"center":True,"timestamp":True}]
    def __init__(self):
        super().__init__()

        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(30)
        self.setSizePolicy(sizePolicy)
        self.setLayout(layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        self.pinnedText = QFrame()
        self.pinnedText.setSizePolicy(sizePolicy)
        self.pinnedText.setLayout(layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.normalText = QFrame()
        self.normalText.setSizePolicy(sizePolicy)
        self.normalText.setLayout(layout)


        layout = QVBoxLayout()
        layout.setContentsMargins(5,5,5,5)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        self.errorText = QFrame()
        self.errorText.setSizePolicy(sizePolicy)
        self.errorText.setLayout(layout)
        

        self.frameDivider = QHLine()
        self.errorDivider = QHLine()
        self.frameDivider.hide()
        self.errorDivider.hide()

        #self.normalText.setStyleSheet("border:3px solid red;")
        #self.pinnedText.setStyleSheet("border:3px solid red;")

        self.normalText.setStyleSheet("border:none;font-size:13px;")
        self.pinnedText.setStyleSheet("border:none;")
        self.errorText.setStyleSheet("border:none;")
        self.normalText.setObjectName("normalText")
        self.pinnedText.setObjectName("pinnedText")
        self.errorText.setObjectName("errorText")
        
        self.pinnedText.hide()
        #self.frameDivider.hide()

        self.container = QFrame()
        self.container.setStyleSheet("border:none;")
        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        self.container.setSizePolicy(sizePolicy)
        self.container.setLayout(layout)
        
        self.container.layout().addWidget(self.frameDivider)
        self.container.layout().addWidget(self.pinnedText)
        self.container.layout().addWidget(self.normalText)
        self.container.layout().addWidget(self.errorDivider)
        self.container.layout().addWidget(self.errorText)

        self.layout().addWidget(self.container)



        self.worldFetchProgress = QProgressBar()
        self.worldFetchProgress.setMinimum(0)
        self.worldFetchProgress.setMaximum(100)
        self.worldFetchProgress.hide()
        
    
        self.worldFetchProgress.setValue(0)

        
        self.layout().addWidget(self.worldFetchProgress)
        
        self.setStyleSheet("""
            background:transparent;
            border-radius:10px;
            border:2px solid gray;
            color:white;
        """)
        self.labels = []
        self.emitText("Welcome to OSRS Ping Checker v0.2",css={"font-weight":"500","color":"lightgray"},flags={"center":True,"perm":True,"title":True})
        #self.emitText("foo")
        #self.emitText("bar")

    def updateProgress(self,progress):
        self.worldFetchProgress.setValue(progress)
        updateStyle(self.worldFetchProgress)

    def setProgressTotal(self,total):
        self.worldFetchProgress.setMaximum(total)
        self.worldFetchProgress.setStyleSheet("""
        QProgressBar {
            color: white;
            font-size:11px;
            font-weight:bold;
        }
        QProgressBar:horizontal {
            border:none;
            border-radius:none;
            border-top:2px solid gray;
            text-align:center;
        }
        QProgressBar::chunk:horizontal {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #007000, stop: 1 #00dd00);
            border-radius:8px;
            border-top-left-radius:0;
            border-top-right-radius:0;
            border-bottom-right-radius:0;
        }
        QProgressBar::chunk:horizontal[value='%d'] {
            border-bottom-right-radius:8px;
        }
        """ % total)
        
        self.worldFetchProgress.show()
        

    #test function
    def animateProgressBar(self):
        self.animation = QtCore.QPropertyAnimation(self.worldFetchProgress,b"value")
        self.animation.setDuration(10000)
        self.animation.setStartValue(self.worldFetchProgress.value())
        self.animation.setEndValue(100)
        self.animation.start()


    def clearErrors(self,errors=[]): #optional to clear select errors
        if errors == []:
            for label in self.errorText.children():
                if type(label) == QVBoxLayout:
                    continue
                self.labels.remove(label)
                label.deleteLater()
            self.errorDivider.hide()

        else:
            deletedLabels=0
            for label in errors:
                if type(label) == QLabel:
                    self.labels.remove(label)
                    label.deleteLater()
                    deletedLabels+=1
                    
            if len(self.errorText.children())-1 == deletedLabels:
                self.errorDivider.hide()
                
        

    def clear(self):
        pinnedLabelsDeleted = 0
        for label in tuple(self.labels):
            self.labels.remove(label)
            label.deleteLater()
            if label.parent().objectName() == "pinnedText":
                pinnedLabelsDeleted+=1

        if len(self.pinnedText.children())-1 == pinnedLabelsDeleted:
            self.pinnedText.hide()
        #    self.frameDivider.hide()
            

    def check(self,worlds,free,members):
        if not free:
            for world in tuple(worlds):
                if world["worldType"] == "Free":
                    worlds.remove(world)
        if not members:
            for world in tuple(worlds):
                if world["worldType"] == "Members":
                    worlds.remove(world)

        for world in worlds[:5]:
            self.emitText(f'World {world["world"]} - {world["players"]} players ({world["worldType"]})')
            
        #print(worlds)

    def emitText(self,text,css={},flags={}):
        if type(text) == list:
            text = "\n".join(text)
        label = QLabel(text)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        label.setSizePolicy(sizePolicy)
        
        


        if "title" in flags and flags["title"]:
            flags["pin"] = True
            self.frameDivider.show()
            addStyle(label,{"margin-top":"5px"})
            self.container.layout().insertWidget(0,label)

        elif "error" in flags and flags["error"]:
            if "specialStyle" not in flags or flags["specialStyle"] == True:
                css.update(self.ERRORSTYLE[0])
                flags.update(self.ERRORSTYLE[1])
            #self.container.layout().addWidget(label)
            self.errorText.layout().addWidget(label)
            self.errorDivider.show()

        elif "pin" in flags and flags["pin"]:
            #if len(self.pinnedText.children()) == 1: #layout counts as child
            #    self.pinnedText.show()
            #    self.frameDivider.show()
            self.pinnedText.show()
            self.pinnedText.layout().addWidget(label)
        else:
            self.normalText.layout().addWidget(label)

        
        if "perm" in flags and not flags["perm"] or "perm" not in flags:
            self.labels.append(label)

        if "timestamp" in flags and flags["timestamp"]:
            text = datetime.now().strftime("%I:%M %p") + ": " + text
            label.setText(text)

        if "center" in flags and flags["center"]:
            label.setAlignment(QtCore.Qt.AlignCenter)


        if css != {}:
            css = makeCSS(css)
        else:
            css = ""

        css+="border:none;"
        
        label.setStyleSheet(css)
        return label

        

        

class Worker(QtCore.QObject):
    #signals
    friendLabelReady = QtCore.pyqtSignal(dict)

    #slots
    @QtCore.pyqtSlot()
    def createFriendLabel(self,data):
        self.friendLabelReady.emit(data)
        

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = QtCore.QThread()
        self.obj = Worker()
        self.typeSelectError = False
        self.initMain()

        self.show()

    def initMain(self):
        uic.loadUi("main.ui",self)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setStyleSheet("""
            #MainWindow {
                background-image:url('osrs.png');
                background-repeat:no-repeat;
            }
            #checkBtn, #clearBtn{
                border:1px solid black;
                border-radius:3.5px;
                padding: 5px 25px 5px 25px;
                background:lightgray;
            }
            #checkBtn:hover, #clearBtn:hover {
                background:silver;
            }
            #checkBtn:pressed, #clearBtn:pressed {
                background:#a0a2a5 !important;
            }

            QCheckBox {
                border:none;
                
            }
            
        """)

        self.con = Console()
        self.clearBtn.pressed.connect(lambda:self.pressBtn(self.clearBtn))
        self.checkBtn.pressed.connect(lambda:self.pressBtn(self.checkBtn))
        self.clearBtn.released.connect(self.clear)
        self.checkBtn.released.connect(self.check)
        self.setFixedSize(335,565)
        #layout = QVBoxLayout()
        #layout.setContentsMargins(0,0,0,0)
        #self.informationBox.setLayout(layout)
        self.informationBox.hide()
        index = self.mainFrame.layout().indexOf(self.informationBox)
        self.mainFrame.layout().insertWidget(index,self.con)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)

    def pressBtn(self,obj):
        obj.setProperty("pressed",True)
        updateStyle(obj)


    def startConCheck(self,worldData):
        self.con.check(worldData,self.freeWorldBox.isChecked(),self.memberWorldBox.isChecked())


    def check(self):
        updateStyle(self.checkBtn)
        if self.freeWorldBox.isChecked() or self.memberWorldBox.isChecked():
            #self.con.clearErrors([self.typeSelectError])
            #self.typeSelectError = False
            self.worldRetriever = WorldFetcher()
            self.worldRetriever.worldSignal.connect(self.startConCheck)
            self.worldRetriever.worldParsedSignal.connect(self.con.updateProgress)
            self.worldRetriever.worldTotalSignal.connect(self.con.setProgressTotal)
            self.con.worldFetchProgress.setFormat("Retrieving world data... (%p%)")
            self.worldRetriever.start()
            
            
            
        else:
            if not self.typeSelectError:
                emittedLabel = self.con.emitText("No world types selected",{},{"timestamp":True,"error":True})
                self.typeSelectError = emittedLabel

    def clear(self):
        updateStyle(self.clearBtn)
        self.con.clear()
        self.con.errorDivider.hide()
        self.typeSelectError = False
                


app = QApplication(sys.argv)
window = Window()

def PyQtException(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = PyQtException

app.exec_()
sys.exit()
