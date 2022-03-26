##Imports
#Python Imports
import tkinter as tk
import random
import threading as t

#League Imports
from lcu_driver import Connector

#Window Code - Basic Blocks 
root = tk.Tk()
root.title('Random Champion Skin')
root.resizable(False, False)

canvas = tk.Canvas(root, width = 500, height = 225)
canvas.pack()

#Global Variables
firstUse = True
filterDefault = tk.IntVar(master = root, value = 0)
autoRandomize = False
modeSelected = False
skinSelected = False

##UI 
#Sets all the UI Elements
def cleanUI():
    global autoRandomize
    
    canvas.delete('all')
        
    if(modeSelected == False):
        infoLabel = tk.Label(root, text = 'Select how you want the Program to Act. \nManual for a Manual Skin Randomization. \nAuto for Automatic Skin Randomization.', fg = 'blue', font = ('helvetica', 12, 'bold'))
        canvas.create_window(250, 50, window = infoLabel)
        
        manualModeButton = tk.Button(root, text = 'Manual Randomize Mode', command = manualStart, bg = 'pink', fg = 'black')
        canvas.create_window(150, 125, window = manualModeButton)
        
        autoModeButton = tk.Button(root, text = 'Auto-Randomize Mode', command = autoRandomizeStart, bg = 'pink', fg = 'black')
        canvas.create_window(350, 125, window = autoModeButton)
    else:
        if(autoRandomize == True):
            autoLabel = tk.Label(root, text = 'Auto Randomizing Skin - Listening for Champion Selection Events', fg = 'blue', font = ('helvetica', 10, 'bold'))
            canvas.create_window(250, 25, window = autoLabel)
        else:
            randomizeButton = tk.Button(root, text = 'Randomize Skin', command = randomizeButtonMethod, bg = 'pink', fg = 'black')
            canvas.create_window(250, 25, window = randomizeButton)
            
        excludeCheckbox = tk.Checkbutton(root, text = 'Exclude Default Skin?', variable = filterDefault)
        canvas.create_window(250, 50, window = excludeCheckbox)
    
##Random Section
#Random Skin Function
async def randomizeSkin(connection):
    global filterDefault
    global errorLabel
    
    random.seed()
    #Gets Skins from Chosen Champion
    skinList = await connection.request('get', '/lol-champ-select/v1/skin-carousel-skins')
    #Converts Json into Json String
    skinListStr = await skinList.json()

    #If it wasn't successful, error will be printed.
    if(len(skinListStr) == 0):
        errorLabel = tk.Label(root, text ='Error: Not in Champion Select or Champion Not Chosen!', fg = 'red', font = ('helvetica', 10, 'bold'))
        canvas.create_window(250, 125, window = errorLabel)
    else:

        #Variables for storage
        skinName = ""
        skinID = 0
        skinIDs = []
        ownedSkinNames = []
        defaultFiltered = False

        #Searches Json for Owned Skins and Sends IDs to List
        for x in skinListStr:
            for key, value in x.items():
                #If we want to filter out the Base Skin
                if(filterDefault.get() == 1 and defaultFiltered == False):
                    defaultFiltered = True
                    break
                else:
                    #Keeps current iteration ID of Skin
                    if(key == 'id'):
                        skinID = value

                    if(key == 'name'):
                        skinName = value

                    #Same as Above
                    if(key == 'ownership'):
                        for y, z in value.items():
                            if(y == 'owned'):
                                if(z == True):
                                    skinIDs.append(skinID)
                                    ownedSkinNames.append(skinName)

        ownedSkinNameTrans = ""
        iteration = 0
        for x in ownedSkinNames:
            if(iteration == 0):
                ownedSkinNameTrans += x + ', '
                iteration += 1
            else:
                ownedSkinNameTrans += x + ', '

        temp = list(ownedSkinNameTrans)
        temp[len(ownedSkinNameTrans) - 2] = ''
        temp[len(ownedSkinNameTrans) - 1] = '.'
        ownedSkinNameTrans = "".join(temp)

        ownedSkinsLabel = tk.Label(root, text = 'Owned Skins: ' + ownedSkinNameTrans, fg = 'blue', font = ('helvetica', 10, 'bold'), wraplength = 500)
        canvas.create_window(250, 125, window = ownedSkinsLabel)

        #Randomly Chooses a Skin
        randNum = random.randint(0, len(skinIDs) - 1)

        pickedSkinLabel = tk.Label(root, text = 'Selected Skin: ' + ownedSkinNames[randNum], fg = 'green', font = ('helvetica', 10, 'bold'))
        canvas.create_window(250, 175, window = pickedSkinLabel)

        #Wrap data into Json format for posting
        data = {
            "selectedSkinId": skinIDs[randNum]
        }

        #Sends Data to League Client
        skinChange = await connection.request('patch', '/lol-champ-select/v1/session/my-selection', data=data)

##Classed Connectors
#Manual Mode
class OneUseConnector():
    #Connector for Class
    connector = Connector()
    
    #Entry for Class
    def __init__(self):
        self.connector.start()

    #For Starting LCU-Driver
    @connector.ready
    async def connect(connection):
        connectionLabel = tk.Label(root, text ='Connection to League Client API Successful!', fg = 'green', font = ('helvetica', 10, 'bold'))
        canvas.create_window(250, 75, window = connectionLabel)
        
        #Randomize
        await randomizeSkin(connection)

    #For Closing LCU-Driver
    @connector.close
    async def close(connection):
        disconnectionLabel = tk.Label(root, text ='Disconnected from League Client API!', fg = 'orange', font = ('helvetica', 10, 'bold'))    
        canvas.create_window(250, 200, window = disconnectionLabel)

#Auto Mode
class StayAliveConnector():
    #Connector for Class
    connector = Connector()
    
    #To Keep the Program from Locking, this is a separated from the program in a thread.
    thread = t.Thread(target = connector.start)
    thread.daemon = True
    
    #Entry for Class
    def start(self):
        self.thread.start()

    #For Starting LCU-Driver
    @connector.ready
    async def connect(connection):
        connectionLabel = tk.Label(root, text ='Connection to League Client API Successful!', fg = 'green', font = ('helvetica', 10, 'bold'))
        canvas.create_window(250, 75, window = connectionLabel)
    
    #Listens for Champion Selection Creation and Deletion
    @connector.ws.register('/lol-champ-select/v1/session', event_types = ('CREATE', 'DELETE',))
    async def inChampSelect(connection, event):
        global skinSelected
        cleanUI()
        
        #Checks which Event Type was triggered. Delete for not in Champion Selection. Create for when in Champion Selection
        if(event.type == 'Delete'):
            ncsLabel = tk.Label(root, text = 'Not In Champion Selection', fg = 'red', font = ('helvetica', 12, 'bold'))
            canvas.create_window(250, 125, window = ncsLabel)
            
            if(skinSelected == True):
                skinSelected = False
        else:
            icsLabel = tk.Label(root, text = 'In Champion Selection, No Champion Selected', fg = 'orange', font = ('helvetica', 12, 'bold'))
            canvas.create_window(250, 125, window = icsLabel)
    
    #Listens for when Summoner chooses Champion
    @connector.ws.register('/lol-champ-select/v1/current-champion', event_types = ('CREATE',))
    async def champSelected(connection, event):
        global skinSelected
        
        #Precautionary Check
        if(event.data != 404):
            if(skinSelected != True):
                cleanUI()
                skinSelected = True
                
                #Randomize
                await randomizeSkin(connection)

    #For Closing LCU-Driver
    @connector.close
    async def close(connection):
        disconnectionLabel = tk.Label(root, text ='Disconnected from League Client API!', fg = 'orange', font = ('helvetica', 10, 'bold'))    
        canvas.create_window(250, 200, window = disconnectionLabel)

##Button Logic
#Starts the OneUseConnector
def randomizeButtonMethod():
    cleanUI()    
    OneUseConnector()

#Function Call to Start Auto Mode and Trigger UI Switch
def autoRandomizeStart():
    global autoRandomize
    global modeSelected
    autoRandomize = True
    modeSelected = True
    
    cleanUI()
    
    sAConnector = StayAliveConnector()
    sAConnector.start()

#Function Call to Trigger UI Switch
def manualStart():
    global modeSelected
    modeSelected = True
    cleanUI()

##Starter
#Applying Starting UI
cleanUI()

#Starts Code
root.mainloop()

