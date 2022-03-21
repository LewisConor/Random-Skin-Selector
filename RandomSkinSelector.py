#League Imports
from lcu_driver import Connector

#Python Imports
import tkinter as tk
import random

#League Code
connector = Connector()

#Random Skin Function
async def randSkin(connection):

    #Gets Skins from Chosen Champion
    skinList = await connection.request('get', '/lol-champ-select/v1/skin-carousel-skins')
    
    #If it wasn't successful, error will be printed.
    if(skinList.status != 200):
        print("Error has occurred")
    else:
        
        #Variables for storage
        skinID = 0
        skinIDs = []
        
        #Converts Json into Json String
        skinListStr = await skinList.json()
        
        #Searches Json for Owned Skins and Sends IDs to List
        for x in skinListStr:
            for key, value in x.items():
                #Keeps current iteration ID of Skin
                if(key == 'id'):
                    skinID = value
                
                #Checks if you own the skin, if so move to array
                if(key == 'ownership'):
                    for y, z in value.items():
                        if(y == 'owned'):
                            if(z == True):
                                skinIDs.append(skinID)
                
        #For Debuging purposes, shows Skin IDs, selects Skin, and shows selected Skin ID
        print('Owned Skin IDs: ', skinIDs)
        randSkinID = skinIDs[random.randint(0, len(skinIDs) - 1)]
        print('Random Skin ID: ', randSkinID)
        
        #Wrap data into Json format for posting
        data = {
            "selectedSkinId": randSkinID
        }
        
        #Sends Data to League Client
        skinChange = await connection.request('patch', '/lol-champ-select/v1/session/my-selection', data=data)

#For Starting LCU-Driver
@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')
    await randSkin(connection)

#For Closing LCU-Driver
@connector.close
async def close(connection):
    print("Connection has been closed.")


#Window Code - Basic Blocks
root = tk.Tk()
root.title('Random Champ Skin')

canvas = tk.Canvas(root, width = 300, height = 100)
canvas.pack()

#Starts the LCU-Driver
def randomise():
    connector.start()

button = tk.Button(text = 'Randomise Skin', command = randomise, bg = 'pink', fg = 'black')
canvas.create_window(150, 50, window = button)

#Starts Code
random.seed()
root.mainloop()