pos = 0
left = 0
right = 0
sleepers = 20
import numpy as np

dataArray = []

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
#
#Result: [2,1,0],[45,1,1],[400,1,1]
#Spit out Table:
#Sleeper    Left    Right
#2          Defect  OK
#45         Defect  Defect
#400        Defect  Defect



while pos < 21:
    currentArray = [pos,left,right]
    dataArray.append(currentArray)
    pos += 1
    
print(dataArray)