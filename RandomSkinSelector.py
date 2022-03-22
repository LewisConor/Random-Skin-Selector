#League Imports
from lcu_driver import Connector

#Python Imports
import tkinter as tk
import random

#League Code
connector = Connector()

#Window Code - Basic Blocks
root = tk.Tk()
root.title('Random Champ Skin')
root.resizable(False, False)

canvas = tk.Canvas(root, width = 500, height = 225)
canvas.pack()

#Global Variables
firstUse = True
filterDefault = tk.IntVar(master = root, value = 0)

#Global Canvas Variables
errorLabel = tk.Label(root, text ='Error: Not in Champion Select or Champion Not Chosen!', fg = 'red', font = ('helvetica', 10, 'bold'))
connectionLabel = tk.Label(root, text ='Connection to League Client API Successful!', fg = 'green', font = ('helvetica', 10, 'bold'))
disconnectionLabel = tk.Label(root, text ='Disconnected from League Client API!', fg = 'orange', font = ('helvetica', 10, 'bold'))

#Random Skin Function
async def randSkin(connection):
    global filterDefault
    global errorLabel
    
    #Gets Skins from Chosen Champion
    skinList = await connection.request('get', '/lol-champ-select/v1/skin-carousel-skins')
    #Converts Json into Json String
    skinListStr = await skinList.json()
    
    #If it wasn't successful, error will be printed.
    if(len(skinListStr) == 0):
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

#For Starting LCU-Driver
@connector.ready
async def connect(connection):
    global connectionLabel
    
    canvas.create_window(250, 75, window = connectionLabel)
    await randSkin(connection)

#For Closing LCU-Driver
@connector.close
async def close(connection):
    global disconnectionLabel
    
    canvas.create_window(250, 200, window = disconnectionLabel)

#Starts the LCU-Driver
def randomise():
    global errorLabel
    global connectionLabel
    global disconnectionLabel
    global firstUse
    global filterDefault

    if(firstUse == True):
        firstUse = False
    else:
        canvas.delete('all')
        
        button = tk.Button(root, text = 'Randomise Skin', command = randomise, bg = 'pink', fg = 'black')
        canvas.create_window(250, 25, window = button)
        
        checkbox = tk.Checkbutton(root, text = 'Exclude Default Skin?', variable = filterDefault)
        canvas.create_window(250, 50, window = checkbox)
        
    connector.start()

button = tk.Button(root, text = 'Randomise Skin', command = randomise, bg = 'pink', fg = 'black')
canvas.create_window(250, 25, window = button)

checkbox = tk.Checkbutton(root, text = 'Exclude Default Skin?', variable = filterDefault)
canvas.create_window(250, 50, window = checkbox)

#Starts Code
random.seed()
root.mainloop()