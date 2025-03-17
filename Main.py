import cv2
import threading
import datetime
import os

class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
        self.cam = cv2.VideoCapture(camID)

    def run(self):
        print(f"Starting {self.previewName}")
        camPreview(self.previewName, self.cam)

def camPreview(previewName, cam):
    """Handles video display and keypress image saving."""
    cv2.namedWindow(previewName)
    
    if not cam.isOpened():
        print(f"Error: Unable to access camera {previewName}")
        return

    rval, frame = cam.read()
    
    while rval:
        cv2.imshow(previewName, frame)
        rval, frame = cam.read()

        key = cv2.waitKey(20)

        if key in [ord('a'), ord('s'), ord('d'), ord('w')]:  
            save_images(key)

        elif key == 27:  # ESC to exit
            break

    cam.release()
    cv2.destroyWindow(previewName)

def save_images(key):
    """Saves images based on the pressed key."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for thread in [thread1, thread2]:
        if thread.cam.isOpened():
            rval, frame = thread.cam.read()
            if rval and frame is not None:
                # Determine file name based on key
                if key == ord('a'):
                    label = "Defect" if thread.previewName == "Left" else "OK"
                elif key == ord('s'):
                    label = "Defect"
                elif key == ord('d'):
                    # 'd' -> Left camera as OK, Right camera as Defect
                    label = "OK" if thread.previewName == "Left" else "Defect"
                elif key == ord('w'):
                    label = "OK"

                if label:  # Only save if label is defined
                    filename = f"{label}_{thread.previewName}_{timestamp}.jpg"
                    path = 'C:/Users/AnthonyLeo/OneDrive - RSRG/Documents/Code/DefectDetector/Images'
                    cv2.imwrite(os.path.join(path, filename), frame)
                    print(f"Saved {filename}")

# Create and start camera threads
thread1 = camThread("Left", 1)
thread2 = camThread("Right", 3)

thread1.start()
thread2.start()

print("\nActive threads:", threading.active_count())





# camera1 = cv2.VideoCapture(1)
# camera2 = cv2.VideoCapture(2)
# while True:
#     return_value,image = camera1.read()
#     return_value,image2 = camera2.read()
#     gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#     cv2.imshow('image',gray)
#     if cv2.waitKey(1)&'0xFF'==ord('s'):
#         cv2.imwrite('test.jpg',image)
#         cv2.imwrite('test2.jpg',image2)
#         break
# camera1.release()
# camera2.release()
# cv2.destroyAllWindows()

#pygame
##dataArray = []

#optical encoder set to zero at start (measures full rotation and records distance travelled)
#Infared sensor set to no sleeper to drive (measures if sleeper is present or not)
#Sleeperflag set to 0 (when set to 0 machine drives)

#while infrared does not see sleeper && sleeper number is less than total sleeper
#   drive forward and record distance
#   if Infrared sees sleeper 
#       while infrared sees sleeper
#           drive maybe plus x amount of steps
#       Swivel out cameras
#       increment sleeper variable by one
#       left and right cameras take photo and return image in left and right variable
#       append currentArray = [pos, left, right] onto array as shown below.
#
#save dataArray in file x
#Run compiling software to analysis array and return position arrays with defect detection.
#Compile(x)
#
#Result: [2,1,0],[45,1,1],[400,1,1]
#Spit out Table:
#Sleeper    Left    Right
#2          Defect  OK
#45         Defect  Defect
#400        Defect  Defect



#while pos < 21:
    #currentArray = [pos,left,right]
    #dataArray.append(currentArray)
    #pos += 1
    
#print(dataArray)