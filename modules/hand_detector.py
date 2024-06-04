import mediapipe as mp
import cv2
import math
import pyautogui

class HandDetector:
    def __init__(self,mode=False,max_hands=1,detection=0.7,track=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.detection = detection
        self.track = track

        self.draw = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hand = self.mp_hands.Hands(self.mode,self.max_hands)
        self.result = None
        self.wFr = None
        self.hFr = None
    
    def findHand(self,img,draw=False):
        self.wFr,self.hFr, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hand.process(img_rgb)
        hand_landmarks = self.results.multi_hand_landmarks
        if hand_landmarks:
            if draw:
                for landmark in hand_landmarks:
                    self.draw.draw_landmarks(img, landmark,self.mp_hands.HAND_CONNECTIONS)

            return img,hand_landmarks
        return img, None
    
    def findPosition(self,hand_landmarks,hand=0):
        positions = []
        
        if hand_landmarks:
            landmarks = hand_landmarks[hand].landmark
            for id,lm in enumerate(landmarks):
                p = (id,round(lm.x*self.wFr),round(lm.y*self.hFr))
                positions.append(p)
        
        if len(positions) == 0:
            return None
        return positions
    
    def findDistance(self,positions,point1,point2):
        if positions:
            x1 = positions[point1][1]
            y1 = positions[point1][2]

            x2 = positions[point2][1]
            y2 = positions[point2][2]

            distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            return distance
        
        return None
    
    def findCentroidDistance(self,positions,points:list):
        coords = [(positions[p][1],positions[p][2]) for p in points]

        x_coords = [c[0]  for c in coords]
        y_coords = [c[1]  for c in coords]

        centroid_x = sum(x_coords) / len(points)
        centroid_y = sum(y_coords) / len(points)
        centroid = (centroid_x,centroid_y)

        return centroid
    
    def fingerTipsTogether(self,positions,points:list,threshold=50):
        coords = [(positions[p][1],positions[p][2]) for p in points]
        centroid = self.findCentroidDistance(positions,points)

        for coord in coords:
            distance = math.sqrt((coord[0] - centroid[0])**2 + (coord[1] - centroid[1])**2)
            # print("fingertips distance--:",distance)
            if distance > threshold:
                return False
        
        return True

    
    def findGesture(self, positions):
        thumb,index,middle,ring,pinky = 0,1,2,3,4 # list index numbers
        tip_ids = [4,8,12,16,20] # 4-thumb, 8-index, 12-ring, 16-middle, 20-pinky
        finger_up = [0,0,0,0,0]

        
        #for thumb finger
        if positions[tip_ids[thumb]][1] < positions[tip_ids[thumb]-1][1]:
            finger_up[thumb] = 1
        
        # if self.findDistance(positions,tip_ids[thumb],tip_ids[middle]-2) <= 50:
        #     finger_up[thumb] = 0

        # for other fingers
        for id in range(1,5):
            if positions[tip_ids[id]][2] < positions[tip_ids[id]-2][2]:
                finger_up[id] = 1
        
        print("finger_up",finger_up)
        if self.fingerTipsTogether(positions,tip_ids,30):
            return "feathers_toggle"
        
        elif finger_up.count(1) == 1:
            # moving mode (only index finder up)
            if finger_up[index] == 1:
                return "moving_mode"
            # elif finger_up[thumb] == 1:
            #     return "confirm_mode"
            
        elif finger_up.count(1) == 2:
            if finger_up[index] == 1 and finger_up[thumb] == 1: # clicking mode (thumb and index finder up)
                return "clicking_mode"
            
            if finger_up[index] == 1 and finger_up[middle] == 1: # clicking mode (index and middle finder up)
                return "scroll_mode"
            
        # elif finger_up.count(1) == 3:
        #     if finger_up[index] == 1 and finger_up[thumb] == 1 and finger_up[middle] == 1:
        #          pyautogui.scroll(clicks=-2.1)

        else:
            return None
        
