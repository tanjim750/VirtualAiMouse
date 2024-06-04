import cv2
from modules import hand_detector as hd
from modules import actions
import pyautogui

wCam,hCam = 680,480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

detector = hd.HandDetector()
make_action = actions.MakeAction(smoothness=0.1)

while True:
    success, img = cap.read()
    hCam,wCam, _ = img.shape
    
    img = cv2.flip(img,1)
    img, landmarks = detector.findHand(img,True)
    if landmarks:
        p = detector.findPosition(landmarks)
        # print("fingertips together:",detector.fingerTipsTogether(p,[4,8],15))
        # print("fingertips distance:",detector.findDistance(p,4,8))

        make_action.action(p)
    cv2.rectangle(img,(150,100),(wCam-150,hCam-100),(250,0,255),2)
    # cv2.imshow("Virtual Mouse frame", img)
    cv2.waitKey(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

