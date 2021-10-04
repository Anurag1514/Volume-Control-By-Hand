import cv2
import time
import numpy as np
import Hand_Tracking_Module as htm
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
print(volume.GetVolumeRange())
print(minVol, maxVol)

vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)

while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])//100
        # print(area)
        if 200 < area < 1400:
            # print("yes")

            # Find distance b/w index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)
            # print(length)

            # Convert Volume

            volBar = np.interp(length, [25, 200], [400, 150])
            volPer = np.interp(length, [25, 200], [0, 100])
            # print(int(length), vol)
            # volume.SetMasterVolumeLevel(vol, None)

            # Reduce Resolution to make it smoother
            smoothness = 20
            volPer = smoothness * round(volPer/smoothness)

            # Check fingers are up
            fingers = detector.fingersUp()

            # If pinky finger is down set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 12, (0, 255, 0), cv2.FILLED)

                if cVol > 80:
                    colorVol = (0, 0, 255)
                else:
                    colorVol = (0, 255, 0)


    # Hand Rage: 50 - 300
    # Volume Range -96 - 0
    # To Convert HandRange to VolumeRange we use numpy
    # Drawing
        if cVol > 80:
            cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (30, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (30, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {cVol}', (500, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colorVol, 2)

    # FrameRate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, f'Fps: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    cv2.imshow("Volume_via_HandControl", img)
    cv2.waitKey(1)

