import numpy as np
import cv2
import os

import time

from imutils import paths

import tensorflow as tf

    
from keras.models import load_model


import destination, trans

ht =60 #thresh value
bgSet = False
bgSubThreshold = 50
learningRate = 0
blurValue = 41  # GaussianBlur parameter

imagefile=destination.images
modelfile =destination.model

listofwords = []

trainsub = "ka"

motion = False
current = "none"
mtime = 0
msettime = 0

imagePaths = list(paths.list_images(imagefile))

labels=[]

# initialize the class labels
for x in imagePaths:
   
    label = x.split(os.path.sep)[-1].split(".")[0].split("-")[0]
    if label not in labels:
        labels.append(label)


CLASSES = labels
CLASSES.sort()
print(CLASSES)

def write(name,image):
    index = 0
    Name = name+"-"+str(index)+".png"
    while Name in os.listdir(imagefile):
        Name = name+"-"+str(index)+".png"
        index += 1
    cv2.imwrite(imagefile+os.path.sep+Name,image)
    print(index)
    


def on_trackbar(a):
    global ht
    ht = a
    print(ht)

def remove_background(frame):
    fgmask = bgModel.apply(frame, learningRate=learningRate)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

def image_to_feature_vector(image, size=(32, 32)):
	# resize the image to a fixed size, then flatten the image into
	# a list of raw pixel intensities
	return cv2.resize(image, size).flatten()




# load the network
print("[INFO] loading network architecture and weights...")

model = load_model(modelfile)

cap = cv2.VideoCapture(0)


cv2.namedWindow("frame")
trackbar_name ="thresh"
cv2.createTrackbar(trackbar_name, "frame" , 0, 255, on_trackbar)

label="Started"
mlabel = "***"

while True:
    ret, frame = cap.read()
    #remove that annoying ulto effect
    frame = cv2.flip(frame, 1)
    
    top, right, bottom, left = 50, 350, 250, 590

    roi = frame[top:bottom, right:left]
    cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
    
    if bgSet:
        img=remove_background(roi)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (blurValue, blurValue), 0)
        ret, thresh = cv2.threshold(blur, ht, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        canvas = np.zeros(gray.shape, np.uint8)
        if(contours):
            contour = max(contours, key=cv2.contourArea)
            #hull = cv2.convexHull(np.float32(contour))
            cv2.drawContours(canvas, contours, -1, (255,255,255), 2)
            
            
            
            features = image_to_feature_vector(canvas) / 255.0
            features = np.array([features])
 
            probs = model.predict(features)[0]
            
            prediction = probs.argmax(axis=0)

            label = CLASSES[prediction]
            frame = cv2.rectangle(frame,(0,0),(100,100),(0,0,0),-1)
            
            
            
            
            if "1" in label:
                if True:
                    motion = True
                    current=label[:-1]
                    msettime= time.time()
            elif "2" in label and motion:
                    if label[:-1]==current and time.time()-msettime<1.5:
                        motion = False
                        mlabel=label[:-1]
                        mtime=time.time()
        cv2.imshow("mini",canvas)
        if mlabel!="***" and time.time()-mtime>2:
            mtime=0
            mlabel="***"
        if "1" not in label and "2" not in label:
                '''cv2.putText(frame, label, (10, 35), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0), 3)'''
                frame=trans.nep(frame,label)
                
        else:
            print(label)
        cv2.putText(frame, "last motion:"+mlabel, (300, 35), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0), 3)
    
   
    if len(listofwords)>0:
        frame = cv2.rectangle(frame,(0,400),(300,500),(1,0,0),-1)
        frame=trans.nepSet(frame, listofwords)
        
        
        
    cv2.imshow("frame",frame)
    wk = cv2.waitKey(1)
    
    if wk == ord('b'):
        print('backgroud set')
        bgModel = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
        bgSet = True
        
    elif wk == ord('s'):
        im = canvas
        write(trainsub,im)

        
    elif wk == ord('a'):
        cap.release()
        cv2.destroyAllWindows()
        break
    
    elif wk == ord('w'):
       
        listofwords.append(label)
        
       
    
    elif wk == ord('e'):
        listofwords=[]

