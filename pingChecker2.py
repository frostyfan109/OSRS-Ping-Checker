from ping3 import ping as Ping
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QFont,QIcon,QPainter,QPen,QPalette,QColor,QPolygonF,QBrush,QPainterPath
from PyQt5 import uic,QtCore
import sys
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup as bs
import tinycss
import time
from pprint import pprint
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import math
import re
from matplotlib.colors import CSS4_COLORS as colors
import random
import logging
from urllib.request import urlopen

#cssutils.log.setLevel(logging.CRITICAL)

colors = list(colors.values())


app = QApplication(sys.argv)
pix = QPixmap(os.path.join("images","splash3.png"))
splash = QSplashScreen(pix,QtCore.Qt.WindowStaysOnTopHint)
splash.show()


with open("config.json","r") as data:
    config = json.load(data)


parser = tinycss.make_parser()
sheet = parser.parse_stylesheet(requests.get("http://www.runescape.com/css/c/oldschool-101.css").text)

class Canvas(FigureCanvas):
    def __init__(self,width=5,height=5,dpi=100):
        figure = Figure()
        self.axes = figure.add_subplot(111)
        FigureCanvas.__init__(self,figure)
        FigureCanvas.updateGeometry(self)

    def plot(self,data):
        x = np.array(data["x"]["data"])
        y = np.array(data["y"]["data"])
        newData = {}
        for x,y in list(zip(x,y)):
            if x in newData:
                newData[x].append(y)
            else:
                newData[x] = [y]
        for i in newData:
            newData[i] = sum(newData[i])/len(newData[i])

        x = []
        y = []
        for key in newData:
            x.append(key)
            y.append(newData[key])
            
        self.axes.bar(x,y)
        self.axes.set_xlabel(data["x"]["title"])
        self.axes.set_ylabel(data["y"]["title"])
        self.draw()

class Sorter(QFrame):
    def __init__(self,categories):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(4,2,4,2)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(layout)
        self.setStyleSheet("margin-top:2.5px;")
        for category in categories:
            categoryWidget = SortCategory(category)
            categoryWidget.setObjectName(category)
            self.layout().addWidget(categoryWidget)
            
        self.setStyleSheet("border-radius:5px;padding:.25px;border:1px solid #8E7246;")
        



class ArrowBtn(QLabel):
    UP = 0
    DOWN = 1
    clickSignal = QtCore.pyqtSignal()
    releaseSignal = QtCore.pyqtSignal()
    def __init__(self,direction):
        super().__init__()
        self.direction = direction
        #self.setFlat(True)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)
        #self.setStyleSheet("background-color:green;border:1px solid green;max-width:12px;max-height:12px;min-width:12px;min-height:12px;border-radius:6px")
        self.setStyleSheet("padding:0;margin:0;")
        self.setFixedSize(16,16)
        
    def paintEvent(self,event):
        painter = QPainter()
        painter.begin(self)
        color = QtCore.Qt.white
        painter.setPen(QPen(QtCore.Qt.gray))
        poly = QPolygonF()
        """
        if self.direction == self.UP:
            circleColor = QtCore.Qt.darkGreen
            poly.append(QtCore.QPoint(4+4,0+6))
            poly.append(QtCore.QPoint(8+4,4+6))
            poly.append(QtCore.QPoint(0+4,4+6))
        elif self.direction == self.DOWN:
            circleColor = QtCore.Qt.red
            poly.append(QtCore.QPoint(4+3,4+6))
            poly.append(QtCore.QPoint(8+3,0+6))
            poly.append(QtCore.QPoint(0+3,0+6))
        """
        if self.direction == self.UP:
            circleColor = QtCore.Qt.darkGreen
            #if self.property("pressed"):
                #circleColor = QColor(0x005600)
            poly.append(QtCore.QPoint(6+2,0+4))
            poly.append(QtCore.QPoint(12+2,6+4))
            poly.append(QtCore.QPoint(0+2,6+4))
        elif self.direction == self.DOWN:
            circleColor = QtCore.Qt.red
            #if self.property("pressed"):
                #circleColor = QtCore.Qt.darkRed
            poly.append(QtCore.QPoint(6+1,6+5))
            poly.append(QtCore.QPoint(12+1,0+5))
            poly.append(QtCore.QPoint(0+1,0+5))

        if self.property("selected"):
            circleColor = QColor(0x666666)
        
        brush = QBrush()
        brush.setStyle(QtCore.Qt.SolidPattern)
        radius = 8
        
        '''
        path = QPainterPath()
        painter.setPen(QPen(QColor(255,255,0)))
        brush.setColor(QColor(255,255,0))
        path.addRect(0,0,radius*2,radius*2)

        painter.fillPath(path,brush)
        '''
        
        path = QPainterPath()
        painter.setPen(QPen(circleColor))
        brush.setColor(circleColor)
        path.addEllipse(0,0,radius*2,radius*2)
        
        painter.fillPath(path,brush)

        
        brush.setColor(color)
        #painter.drawPolygon(poly)
        path = QPainterPath()
        path.addPolygon(poly)
        painter.fillPath(path,brush)

        
        painter.end()


    def deselect(self):
        self.setProperty("selected",False)
        self.repaint()


    def mousePressEvent(self,event):
        self.clickSignal.emit()

    def mouseReleaseEvent(self,event):
        self.releaseSignal.emit()


class SortCategory(QFrame):
    pressedSignal = QtCore.pyqtSignal(int)
    def __init__(self,category):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(1,1,1,1)
        self.setLayout(layout)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)
        #self.setStyleSheet("QFrame{border:1px solid red;}QFrame > *{}")
        self.setStyleSheet("border:none;")
        self.upArrow = ArrowBtn(ArrowBtn.UP)
        #self.upArrow.pressed.connect(lambda:self.click(self.upArrow))
        #self.upArrow.released.connect(lambda:self.unclick(self.upArrow))
        self.upArrow.clickSignal.connect(lambda:self.click(self.upArrow))
        self.upArrow.releaseSignal.connect(lambda:self.unclick(self.upArrow))
        #sizePolicy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        #self.upArrow.setSizePolicy(sizePolicy)
        #self.upArrow.setFixedSize(12,12)
        
        
        self.downArrow = ArrowBtn(ArrowBtn.DOWN)
        #self.downArrow.pressed.connect(lambda:self.click(self.downArrow))
        #self.downArrow.released.connect(lambda:self.unclick(self.downArrow))
        self.downArrow.clickSignal.connect(lambda:self.click(self.downArrow))
        self.downArrow.releaseSignal.connect(lambda:self.unclick(self.downArrow))
        
        self.categoryLabel = QLabel(category)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.categoryLabel.setSizePolicy(sizePolicy)
        self.categoryLabel.setStyleSheet("font-weight:bold;margin-bottom:5px;")
        
        self.layout().addWidget(self.upArrow)
        self.layout().addWidget(self.downArrow)
        self.layout().addWidget(self.categoryLabel)
        #self.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def click(self,widget):        
        widget.setProperty("selected",True)
        if widget.direction == widget.UP:
            self.downArrow.deselect()
        elif widget.direction == widget.DOWN:
            self.upArrow.deselect()
        self.pressedSignal.emit(self.direction)
        widget.setProperty("pressed",True)
        widget.repaint()

    def unclick(self,widget):
        widget.setProperty("pressed",False)
        widget.repaint()



class PopupGraph(QDialog):
    def __init__(self,graphData):
        super().__init__()
        self.graphData = graphData
        self.setWindowTitle(graphData["title"])
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        self.setSizePolicy(sizePolicy)
        self.setLayout(layout)
        self.canvas = Canvas(graphData)
        self.canvas.plot(graphData)
        self.layout().addWidget(self.canvas)
        
        self.exec()


class WorldFetcher(QtCore.QObject):
    worldSignal = QtCore.pyqtSignal(list)
    worldParsedSignal = QtCore.pyqtSignal(int)
    worldTotalSignal = QtCore.pyqtSignal(int)
    fetchingCompleteSignal = QtCore.pyqtSignal()
    pingTotalSignal = QtCore.pyqtSignal(int)
    worldPingedSignal = QtCore.pyqtSignal(int)
    pingDeltasSignal = QtCore.pyqtSignal(dict)
    worldListComplete = QtCore.pyqtSignal(list)
    
    def __init__(self):
        QtCore.QObject.__init__(self)


    @QtCore.pyqtSlot()
    def run(self):
        worlds = self.getWorlds()
        self.worldSignal.emit(worlds)


    def pingWorlds(self,worlds):
        #pprint(worlds)
        #self.fetchingCompleteSignal.emit()
        self.pingTotalSignal.emit(len(worlds))
        times = {"title":"Latency by country","x":{"title":"Country","data":[]},"y":{"title":"Latency","data":[]}}
        for pingCount,world in enumerate(tuple(worlds),1):
            oldTime = time.time()
            worldNumber = world["world"]-300
            ping = getServerPing(worldNumber)
            if ping == None:
                worlds.remove(world)
                continue
            world["ping"] = math.floor(ping)
            self.worldPingedSignal.emit(pingCount)
            delta = time.time()-oldTime
            times["x"]["data"].append(world["country"])
            times["y"]["data"].append(ping)
        self.fetchingCompleteSignal.emit()
        if config["debugGraphs"]:
            self.pingDeltasSignal.emit(times)
        self.worldListComplete.emit(worlds)
        
    
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
            className = worldChildren[2]["class"][-1]
            worldType = worldChildren[3].string
            worldActivity = worldChildren[4].string

            if worldActivity == "-":
                worldActivity = ""

            worldNumber = int(worldInfo.find("a")["id"].split("-")[-1])
            if worldNumber-300 != int(worldInfo.find("a").string.split()[-1]):
                print("Error:",worldNumber,"(-300)","!=",worldInfo.find("a").string.split()[-1])

        
            parsedWorlds.append({"cssClass":className,"world":worldNumber,"players":players,"country":country,"worldType":worldType,"worldActivity":worldActivity})
            self.worldParsedSignal.emit(worldCount)
            time.sleep(0.005)
        return parsedWorlds


def saveConfig():
    with open("config.json","w") as data:
        json.dump(config,data)

def getServerPing(world):
    url = f"oldschool{world}.runescape.com"
    ping = Ping(url)
    if ping == None:
        return None
        print("Error:",url,"returned none")
    return ping*1000


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


def countryImages(worlds):
    '''
    countries = set([i["country"] for i in worlds])
    colorDict = {}
    for country in countries:
        random.shuffle(colors)
        colorDict[country] = colors.pop()
    return colorDict
    '''
    
    countryClasses = set([i["cssClass"] for i in worlds])
    imageUrlDict = {}
    for countryClass in countryClasses:
        imageUrlDict[countryClass] = download(getImageURL(countryClass))[0]
    return imageUrlDict


def getImageURL(imgClass):
    imgClass = "."+imgClass
    rule = [rule for rule in sheet.rules if imgClass in rule.selector.as_css()][0]
    return re.search("(?<=\().*?(?=\))",[declaration.value for declaration in rule.declarations if declaration.name=="background-image"][0].as_css()).group(0)[1:-1]
    
def download(url,name=None):
    if name != None:
        filename = name
    else:
        filename = url.split('/')[-1]
    filename = os.path.join("images",filename)
    if os.path.isfile(filename) == False:
        img_file = open(filename, "wb")
        img_file.write(urlopen(url).read())
        img_file.close()
        absolute_path = os.path.dirname(os.path.abspath(filename))
        return filename, absolute_path
    else:
        absolute_path = os.path.dirname(os.path.abspath(filename))
        return filename, absolute_path

class QHLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("border:none;border-top:1px solid gray;")

class Console(QFrame):
    worldPingList = QtCore.pyqtSignal(list)
    ERRORSTYLE = [{"color":"red"},{"center":True,"timestamp":True}]
    def __init__(self):
        super().__init__()

        self.images = None
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(30)
        self.setSizePolicy(sizePolicy)
        self.setLayout(layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        self.pinnedText = QFrame()
        self.pinnedText.setSizePolicy(sizePolicy)
        self.pinnedText.setLayout(layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setAlignment(QtCore.Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
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
        self.pinnedText.setStyleSheet("border;")
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

        self.scrollContainer = QScrollArea()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.scrollContainer.setSizePolicy(sizePolicy)
        self.scrollContainer.setWidget(self.normalText)
        self.scrollContainer.setWidgetResizable(True)
        self.scrollContainer.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff) 
        self.scrollContainer.setStyleSheet("""

            QScrollBar:vertical {
                border: 1px solid darkgray;
                background: white;
                width: 15px;
                margin: 16px 0 16px 0;
            }
            QScrollBar::handle:vertical {
                background: lightgray;
                min-height: 20px;
                border-top:1px solid darkgray;
                border-bottom:1px solid gray;
            }
            QScrollBar::add-line:vertical {
                border: 1px solid darkgray;
                background: white;
                height: 15px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::sub-line:vertical {
                border:1px solid darkgray;
                background: white;
                height: 15px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                
            }
            QScrollBar::up-arrow:vertical {
                background: url("images/up-arrow.png");
                
            }
            QScrollBar::down-arrow:vertical {
                background: url("images/down-arrow.png");
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollArea[worldList=true] {
                /*background:#362D1A;*/
            }
        """)
        
        
        self.container.layout().addWidget(self.frameDivider)
        self.container.layout().addWidget(self.pinnedText)
        self.container.layout().addWidget(self.scrollContainer)
        #self.container.layout().addWidget(self.normalText)
        self.container.layout().addWidget(self.errorDivider)
        self.container.layout().addWidget(self.errorText)

        self.layout().addWidget(self.container)



        self.worldFetchProgress = QProgressBar()
        self.worldFetchProgress.setMinimum(0)
        self.worldFetchProgress.setMaximum(100)
        self.worldFetchProgress.hide()
        #self.animateProgressBar()
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
        QProgressBar::chunk:horizontal[done=true] {
            border-bottom-right-radius:8px;
        }
        """)
        
    
        self.worldFetchProgress.setValue(0)

        
        self.layout().addWidget(self.worldFetchProgress)
        
        self.setStyleSheet("""
            background:transparent;
            border-radius:10px;
            border:2px solid gray;
            color:white;
        """)
        self.labels = []
        self.emitText("Welcome to OSRS Ping Checker v0.4",css={"font-weight":"500","color":"lightgray"},flags={"center":True,"perm":True,"title":True})
        #self.emitText("foo")
        #self.emitText("bar")
            
            
        
    
    def completeWorldData(self,worlds):
        #pprint(worlds)
        #label = self.emitText("Worlds with Best Ping:",css={"text-decoration":"underline","color":"gray","font-weight":"bold","font-size":"14"},flags={"center":True,"pin":True})
        #index = self.pinnedText.layout().indexOf(label)+1
        categories = ["foo"]
        #self.sorter = Sorter(categories)
        #print(self.sorter.findChild(QFrame,"foo"))
        
            
        self.pinnedText.show()
        #self.pinnedText.layout().addWidget(self.sorter)
        #self.sorter = Sorter(["foo"])
        #self.normalText.layout().insertWidget(0,self.sorter)
        #self.labels.append(self.sorter)
        self.scrollContainer.setProperty("worldList",True)
        updateStyle(self.scrollContainer)
        if self.images == None:
            self.images = countryImages(worlds)

        worlds = sorted(worlds,key=lambda k:k["ping"])
        pingColors = {range(0,25):"#00ff00",range(26,50):"#00a500",range(51,100):"#b2f733",range(101,150):"#ffe500",range(151,200):"#ff8800"}
        
        for world in worlds:
            key = [i for i in list(pingColors.keys()) if world["ping"] in i]
            if len(key) == 0:
                pingColor = "#e01616"
            else:
                pingColor = pingColors[key[0]]
            #print(world)
            #self.emitText(f'<span style="background-image:{self.images[world["cssClass"]]};">&nbsp;{world["country"]}</span><span>World {world["world"]}: {math.floor(world["ping"])} ping</span>',flags={"rich":True})
            label = self.emitText(f'''
                <img src="{self.images[world["cssClass"]]}">
                <span>
                    World {world["world"]}: <span style="color:{pingColor};">{world["ping"]} ping</span>
                </span>
                <img src="images/{world["worldType"].lower()}.gif">
                <span>
                    {world["worldActivity"]}
                </span>
            ''',flags={"rich":True})
            label.setProperty("worldLabel",True)
             
            

    def emitWorldLabel(self,labelData):
        worldLabelText = labelData

    def resetThreadedFetching(self):
        self.worldFetchProgress.setProperty("done",False)
        updateStyle(self.worldFetchProgress)
        self.worldFetchProgress.setValue(0)
        self.worldFetchProgress.setFormat("%p%")
        self.worldFetchProgress.hide()

    def updateProgress(self,progress):
        self.worldFetchProgress.setValue(progress)
        updateStyle(self.worldFetchProgress)
        if progress == self.worldFetchProgress.maximum():
            self.worldFetchProgress.setProperty("done",True)
            updateStyle(self.worldFetchProgress)
            self.resetThreadedFetching()

    def setProgressTotal(self,total,title):
        self.worldFetchProgress.setMaximum(total)
        self.worldFetchProgress.setFormat(title)
        titleStr = re.sub(r"%.|\(([^)]+)\)","",title)
        self.emitText(titleStr)
        self.worldFetchProgress.show()
        

    #test function
    def animateProgressBar(self):
        #have to store the animation or it will get garbage collected and wont execute
        '''
        self.animation = QtCore.QPropertyAnimation(self.worldFetchProgress,b"value")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.start()
        '''

        #self.animation = QtCore.QPropertyAnimation(self.worldFetchProgress,b"opacity")


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

        self.scrollContainer.setProperty("worldList",False)
        updateStyle(self.scrollContainer)
            

    def check(self,worlds,free,members):
        if not free:
            for world in tuple(worlds):
                if world["worldType"] == "Free":
                    worlds.remove(world)
        if not members:
            for world in tuple(worlds):
                if world["worldType"] == "Members":
                    worlds.remove(world)

        self.worldPingList.emit(worlds)        
        #for world in worlds[:5]:
        #    self.emitText(f'World {world["world"]} - {world["players"]} players ({world["worldType"]})')
            
        #print(worlds)

    def emitText(self,text,css={},flags={}):
        if type(text) == list:
            text = "\n".join(text)
        label = QLabel()
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

        if "center" in flags and flags["center"]:
            label.setAlignment(QtCore.Qt.AlignCenter)


        if css != {}:
            css = makeCSS(css)
        else:
            css = ""

        css+="border:none;"
        if "rich" in flags and flags["rich"]:
            label.setTextFormat(QtCore.Qt.RichText)
        label.setText(text)
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
    fetchWorldsSignal = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.obj = Worker()
        self.typeSelectError = False
        self.initMain()

        self.show()

    def initMain(self):
        uic.loadUi("main.ui",self)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setStyleSheet("""
            #MainWindow {
                background-image:url('images/osrs.png');
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
        
        self.createWorkerThread()

        self.memberWorldBox.setChecked(config["worldTypes"]["members"])
        self.freeWorldBox.setChecked(config["worldTypes"]["free"])
        self.memberWorldBox.setProperty("worldType","members")
        self.freeWorldBox.setProperty("worldType","free")
        self.memberWorldBox.clicked.connect(lambda:self.checkBoxClicked(self.memberWorldBox))
        self.freeWorldBox.clicked.connect(lambda:self.checkBoxClicked(self.freeWorldBox))
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


    def createWorkerThread(self):
        self.thread = QtCore.QThread()
        self.worldRetriever = WorldFetcher()
        self.worldRetriever.worldSignal.connect(self.startConCheck)
        self.worldRetriever.moveToThread(self.thread)
        self.thread.start()

        self.fetchWorldsSignal.connect(self.worldRetriever.run)

        self.con.worldPingList.connect(self.worldRetriever.pingWorlds)
        self.worldRetriever.worldParsedSignal.connect(self.con.updateProgress)
        self.worldRetriever.worldTotalSignal.connect(lambda total:self.con.setProgressTotal(total,"%p% Retrieving world data..."))
        self.worldRetriever.fetchingCompleteSignal.connect(self.fetchingComplete)
        self.worldRetriever.pingTotalSignal.connect(lambda total:self.con.setProgressTotal(total,"%p% Retrieving server latency data... (%v/%m)"))
        self.worldRetriever.worldPingedSignal.connect(self.con.updateProgress)
        self.worldRetriever.pingDeltasSignal.connect(self.graph)
        self.worldRetriever.worldListComplete.connect(self.con.completeWorldData)


    def checkBoxClicked(self,obj):
        config["worldTypes"][obj.property("worldType")] = obj.isChecked()
        saveConfig()

    def graph(self,data):
        popup = PopupGraph(data)
        

    def resetWorker(self):
        if self.thread.isRunning():
            self.worldRetriever.disconnect()
            print("terminating")
            self.thread.terminate()

            self.thread.wait()

            self.createWorkerThread()


    def pressBtn(self,obj):
        obj.setProperty("pressed",True)
        updateStyle(obj)


    def startConCheck(self,worldData):
        self.con.check(worldData,self.freeWorldBox.isChecked(),self.memberWorldBox.isChecked())


    def cancel(self):
        self.resetWorker()
        self.checkBtn.setText("Check")
        self.checkBtn.released.disconnect()
        self.checkBtn.released.connect(self.check)
        self.con.resetThreadedFetching()
        self.con.emitText("Cancelling...")
        
        
    def fetchingComplete(self):
        self.checkBtn.setText("Check")
        self.checkBtn.released.disconnect()
        self.checkBtn.released.connect(self.check)
        self.con.resetThreadedFetching()
        self.con.clear()

    def check(self):
        updateStyle(self.checkBtn)
        if self.freeWorldBox.isChecked() or self.memberWorldBox.isChecked():
            #self.con.clearErrors([self.typeSelectError])
            #self.typeSelectError = False
            #self.con.worldFetchProgress.setFormat("Retrieving world data... (%p%)")
            #QtCore.QMetaObject.invokeMethod(self.worldRetriever,"run")
            self.con.worldFetchProgress.show()
            self.fetchWorldsSignal.emit()
            self.checkBtn.setText("Cancel")
            self.checkBtn.released.disconnect()
            self.checkBtn.released.connect(self.cancel)

            
            
            
        else:
            if not self.typeSelectError:
                emittedLabel = self.con.emitText("No world types selected",{},{"timestamp":True,"error":True})
                self.typeSelectError = emittedLabel

    def clear(self):
        updateStyle(self.clearBtn)
        self.con.clear()
        self.con.errorDivider.hide()
        self.typeSelectError = False
                



window = Window()
splash.hide()

def PyQtException(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = PyQtException

app.exec_()
sys.exit()
