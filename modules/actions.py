import pyautogui
from modules import hand_detector as hd
import numpy as np
import math
import time

class MakeAction:
    def __init__(self,camWidth=640,camHeight=480,smoothness = 0.2):
        self.smoothness = smoothness
        self.detector = hd.HandDetector()
        self.camWidth = camWidth
        self.camHeight = camHeight
        self.screenWidth, self.screenHeight = pyautogui.size()
        
        self.prevClickTime = None
        self.crntClickTime = None
        self.dubbleClick = False
        self.mouseDown = False
        self.holdGesture = False
        self.allFeatures = True
        self.clocX, self.clocY = 0,0 # pointer location
        self.plocX, self.plocY = 0,0 # pointer location
        self.cSlLocX, self.cSlLocY = 0,0   # scroll finger location
        self.pSlLocX, self.pSlLocY = 0,0   # scroll finger location
        self.crntScrolltime = None
        self.prevScrolltime = None
        self.alreadyClicked = False
        self.alreadyFeToggled = False
        self.alreadyCopied = False
        self.alreadyPasted = False
        self.alreadyConfirmed = False

        pyautogui.FAILSAFE = False

    def action(self, position):
        if position:
            gesture = self.detector.findGesture(position)
            if gesture is not None:
                # print(gesture,"\nself.alreadyFeToggled: ",self.alreadyFeToggled,"\nself.allFeatures: ",self.allFeatures)
                if gesture == "clicking_mode" and self.allFeatures:
                    self.alreadyCopied = False
                    self.alreadyPasted = False
                    self.alreadyFeToggled = False
                    self.alreadyConfirmed = False
                    self.leftClick(position)
                    
                elif gesture == "moving_mode" and self.allFeatures:
                    self.alreadyCopied = False
                    self.alreadyPasted = False
                    self.alreadyFeToggled = False
                    self.alreadyConfirmed = False
                    self.move(position)

                elif gesture == "feathers_toggle":
                    self.alreadyCopied = False
                    self.alreadyPasted = False
                    self.alreadyConfirmed = False

                    if self.alreadyFeToggled is False:
                        self.alreadyFeToggled = True

                        if self.allFeatures:
                            self.allFeatures = False
                        else:
                            self.allFeatures = True

                elif gesture == "copy_mode":
                    if self.alreadyCopied is False:
                        self.alreadyFeToggled = False
                        self.alreadyCopied = True
                        self.alreadyConfirmed = False
                        self.alreadyPasted = False
                        pyautogui.hotkey('ctrl', 'c')

                elif gesture == "paste_mode":
                    if self.alreadyPasted is False:
                        self.alreadyFeToggled = False
                        self.alreadyCopied = False
                        self.alreadyConfirmed = False
                        self.alreadyPasted = True
                        pyautogui.hotkey('ctrl', 'v')
                
                elif gesture == "confirm_mode":
                    if self.alreadyConfirmed is False:
                        self.alreadyFeToggled = False
                        self.alreadyCopied = False
                        self.alreadyPasted = False
                        self.alreadyConfirmed = True
                        pyautogui.press('enter')
                
                elif gesture == "scroll_mode":
                    self.alreadyCopied = False
                    self.alreadyPasted = False
                    self.alreadyFeToggled = False
                    self.alreadyConfirmed = False
                    self.scroll(position)


                else:
                    self.alreadyCopied = False
                    self.alreadyPasted = False
                    self.alreadyFeToggled = False
                    self.alreadyConfirmed = False
                    
        
        return True
    
    def moveToCoords(self,coordX,coordY):
        x1 = int(np.interp(coordX, (150,self.camWidth-150), (0,self.screenWidth)))
        y1 = int(np.interp(coordY, (100,self.camHeight-100), (0,self.screenHeight)))

        self.clocX = self.plocX + ( x1- self.plocX )* self.smoothness
        self.clocY = self.plocY + ( y1- self.plocY )* self.smoothness

        if abs((self.clocX+self.clocY)/2 - (self.plocX+self.plocY)/2) > 5:
            pyautogui.moveTo(self.clocX,self.clocY)

        self.plocX, self.plocY = self.clocX,self.clocY

        return True

    def move(self, position): # Move to index finger position
        x1 = position[8][1]
        y1 = position[8][2]
        x2 = int(np.interp(x1, (150,self.camWidth-150), (0,self.screenWidth)))
        y2 = int(np.interp(y1, (100,self.camHeight-100), (0,self.screenHeight)))
        
        self.clocX = self.plocX + ( x2- self.plocX )* self.smoothness
        self.clocY = self.plocY + ( y2- self.plocY )* self.smoothness

        # print("before: ",x2,y2)
        # if x2 > self.screenWidth:
        #     x2 = self.screenWidth-5
        
        # if y2 > self.screenHeight:
        #     y2 = self.screenHeight-5

        if abs((self.clocX+self.clocY)/2 - (self.plocX+self.plocY)/2) > 5:
            pyautogui.moveTo(self.clocX,self.clocY)

        self.plocX, self.plocY = self.clocX,self.clocY
        # time.sleep(0.11)

        return True
    
    def leftClick(self,position):
        thumb = 4
        index = 8
        # distance = self.detector.findDistance(position,thumb,index)
        points = (thumb,index)
        fingerTogether = self.detector.fingerTipsTogether(position,points,20)

        if fingerTogether and self.alreadyClicked is False:
            self.crntClickTime = time.time()
            clickTimeDiff = None

            if self.prevClickTime is not None:
                clickTimeDiff = self.crntClickTime - self.prevClickTime
            
            print("clickTimeDiff: ", clickTimeDiff)

            if clickTimeDiff and int(clickTimeDiff*100) <= 65:
                pyautogui.mouseDown(button='left')
                self.mouseDown = True
            else:
                if self.mouseDown:
                    pyautogui.mouseUp(button='left')
                    self.mouseDown = False

                pyautogui.click()
                
            self.alreadyClicked = True
            self.prevClickTime = self.crntClickTime
            time.sleep(0.3)

        elif fingerTogether is False and self.alreadyClicked is True:
            self.alreadyClicked = False

        return True
    
    def hold(self,position):
        thumb = 4
        index = 8
        # distance = self.detector.findDistance(position,thumb,index)
        points = (thumb,index)
        fingerTogether = self.detector.fingerTipsTogether(position,points,20)
        centroid = self.detector.findCentroidDistance(position,list(points))

        # print("hold finger together: ",fingerTogether)

        if fingerTogether and self.dubbleClick:
            if self.mouseDown is False:
                pyautogui.mouseDown(button='left')
                self.mouseDown = True
            self.moveToCoords(centroid[0],centroid[1])

        elif fingerTogether is False and self.mouseDown is True:
            pyautogui.mouseUp(button='left')
            self.mouseDown = False
            self.dubbleClick = False

        return True
    
    def scroll(self,position):
        index = 8
        middle = 12
        points = (index, middle)

        fingerTogether = self.detector.fingerTipsTogether(position,points,30)
        centroid = self.detector.findCentroidDistance(position,points)

        x1 = centroid[0]
        y1 = centroid[1]


        if fingerTogether:
            print("scroll happened....")
            self.crntScrolltime = time.time()
            self.cSlLocX, self.cSlLocY = x1,y1

            if self.prevScrolltime and (self.crntScrolltime - self.prevScrolltime) >= 0.3:
                print("scroll conditioning: ",abs(self.cSlLocX - self.pSlLocX))
                if abs(self.cSlLocX - self.pSlLocX) >= 5:
                    print("scroll happening....")
                    if self.cSlLocX > self.pSlLocX:
                        pyautogui.scroll(clicks=-3.33)
                    else:
                        pyautogui.scroll(clicks=3.33)
                        
            self.pSlLocX, self.pSlLocY = self.cSlLocX, self.cSlLocY
            self.prevScrolltime = self.crntScrolltime
        
        return True
            

        