import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
###############################
wCam,hCam=640,480
###############################
cap=cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime=0

detector=htm.handDetector(detectionCon=0.7,maxHands=1)

devices=AudioUtilities.GetSpeakers()
interface=devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
volume=cast(interface,POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()

minVol=volRange[0]
maxVol=volRange[1]
vol=0
volBar=400
volPer=0
area=0
colorVol=(255,0,0)
while True:
    success,img=cap.read()
    # Find hand
    img=detector.findHands(img)
    lmlist,bbox=detector.findPosition(img,draw=True)
    # print(lmlist)
    if len(lmlist)!=0:

        #Filter based on size
        # print(bbox)
        area=(bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        # print(area)
        if 250<area<1000:

            #find distance between index and thumb
            length,img,lineInfo=detector.findDistance(4,8,img)
            # print(length)
            #convert volume
            # vol=np.interp(length,[20,210],[minVol,maxVol])
            volBar=np.interp(length,[17,210],[400,150])
            volPer=np.interp(length,[17,210],[0,100])
            # print(int(length),vol)
            # volume.SetMasterVolumeLevel(vol,None)


            #Reduce Resolution to make it smoother
            smoothness=10
            volPer=smoothness*round(volPer/smoothness)
            #check fingers up
            fingers=detector.fingersup()
            # print(fingers)
            #if pinky is down set the volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer/100,None)
                cv2.circle(img,(lineInfo[4],lineInfo[5]),13,(0,255,0),cv2.FILLED)
                colorVol=(0,255,0)
            else:
                colorVol=(255,0,0)
           

            # print(lmlist[4],lmlist[8])
            #getting x and y cordinates of the landmarks
            # x1,y1=lmlist[4][1],lmlist[4][2]
            # x2,y2=lmlist[8][1],lmlist[8][2]
            # cx,cy=(x1+x2)//2,(y1+y2)//2

            # cv2.circle(img,(x1,y1),13,(255,0,255),cv2.FILLED)
            # cv2.circle(img,(x2,y2),13,(255,0,255),cv2.FILLED)
            # cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)
            # cv2.circle(img,(cx,cy),10,(255,0,255),cv2.FILLED)
            # length=math.hypot(x2-x1,y2-y1)
            # print(length)
           
            
                



     #Drawings
    cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
    cv2.rectangle(img,(50,int(volBar)),(85,400),(255,0,0),cv2.FILLED)
    cv2.putText(img,f"{int(volPer)} %",(40,450),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),3)
    cVol=int((volume.GetMasterVolumeLevelScalar()*100)+1)
    cv2.putText(img,f"Vol Set: {int(cVol)}",(400,50),cv2.FONT_HERSHEY_COMPLEX,1,colorVol,2)
    #Show the fps on the screen
     #Frame rate
    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime

    cv2.putText(img,f"FPS: {int(fps)}",(40,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)

    cv2.imshow("Webcam",img)
    key=cv2.waitKey(1)
    if key==ord('q'):
        break