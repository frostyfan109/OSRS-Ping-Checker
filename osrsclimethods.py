import requests
import math
import time
import sys
import aioping
import asyncio
from bs4 import BeautifulSoup as bs
from threading import Thread
from pyfiglet import Figlet
import const

#stolen from https://stackoverflow.com/a/34325723
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 0, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    line = '\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix)
    print(line,end='\r')
    if iteration == total: 
        #print()
        print(" "*len(line),end="\r")

class ThreadedConsoleHandler(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.progress = 0
        self.progressTotal = 0
        self.started = False
        self.suffix = ""
        self.done = False

        print(Figlet(font='slant').renderText('OSRS Ping Checker v'+const.VERSION))

    def startProgress(self,msg):
        self.started = msg
        self.done = False

    def endProgress(self):
        self.started = False
        self.progress = 0
        self.progressTotal = 0
        self.done = True

    def run(self):
        delta = time.time()
        while True:
            if self.started != False:
                printProgressBar(self.progress, self.progressTotal, prefix = self.started, suffix=self.suffix, length = 50)
                if self.progress == self.progressTotal:
                    self.endProgress()
            #time.sleep(.01)
            delta = time.time()

async def getServerPing(world):
    url = f"oldschool{world}.runescape.com"
    ping = await aioping.ping(url)
    if ping == None:
        return None
        print("Error:",url,"returned none")
    return ping*1000

async def pingWorld(worlds,world,pingCount,worldPingedCallback):
    worldNumber = world["world"]-300
    #threadCon.suffix = "Pinging world "+str(worldNumber)+""
    #print("Started pinging world", worldNumber)
    ping = await getServerPing(worldNumber)
    pingCount[0] += 1
    #print("Finished pinging world", worldNumber)
    if ping == None:
        worlds.remove(world)
        return
    world["ping"] = math.floor(ping)
    worldPingedCallback(world,pingCount[0])

def pingWorlds(worlds,worldPingedCallback):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    reqs = []
    pingCount = [1]
    for world in tuple(worlds):
        reqs.append(pingWorld(worlds,world,pingCount,worldPingedCallback))

    tasks = asyncio.gather(*reqs)

    loop.run_until_complete(tasks)
    
    return worlds


def filterWorlds(worlds,free,members):
    if not free:
        for world in tuple(worlds):
            if world["worldType"] == "Free":
                worlds.remove(world)
    if not members:
        for world in tuple(worlds):
            if world["worldType"] == "Members":
                worlds.remove(world)
    return worlds


def getWorlds(threadCon):
    html = requests.get("http://oldschool.runescape.com/slu").text
    soup = bs(html,"html.parser")

    worldWrapper = soup.find_all(attrs={"class":"server-list__body"})[0]
    worlds = worldWrapper.findChildren("tr")


    parsedWorlds = []
    totalWorlds = len(worlds)
    threadCon.progressTotal = totalWorlds
    threadCon.startProgress("Fetching world data:")
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

        threadCon.progress = worldCount
        parsedWorlds.append({"cssClass":className,"world":worldNumber,"players":players,"country":country,"worldType":worldType,"worldActivity":worldActivity})
        time.sleep(0.01)
    return parsedWorlds
