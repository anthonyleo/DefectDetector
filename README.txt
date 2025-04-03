README File
Authur: Anthony Leo
Date: 03/04/2025
***************************************************************************
Start Up Process
***************************************************************************
1. Open Terminal
2. Place the terminal in the bottom middle position of the screen.
3. Copy and Paste '' and press enter
4. Enter your starting chainage number as your reference point
5. Camera feeds for left and right camera will open
6. Left click mouse into either of these camera feed windows
7. Travel along the rail to your inspection point (Hall Effect sensor will be incrementing distance as the wheel turns on the rail)
8. Pull inspection cameras below rail for inspection using the lever arms on the mechanism
9. Enter one of the following keyboard bindings depending on the situation:
      'a' - Left camera DEFECT, Right camera OK
      's' - Left camera DEFECT, Right camera DEFECT
      'w' - Left camera OK, Right camera DEFECT
      'd' - Left camera OK, Right camera OK

      Images will be saved of both camera feeds into the plugged in USB drive along with data saved into a txt file in the same USB drive.
10. Continue steps 7-9 until you reach the start of a new chainage point (reference point)
11. Once at your new chainage start position enter the following keyboard binding:
      'c' - The program terminal will ask you to enter a new chainage reference number
            Left click into the terminal and enter the new chainage reference number
            After this has been entered ensure you left click back into the camera feed to use the save image key bindings.
12. Continue until completed works for the day.
13. To end the programe press the 'escape' key and wait for the code to close and camera windows to close.
***************************************************************************
Assessing Data
***************************************************************************
1. Ensure the raspberry pi is turned off
2. Remove the USB stick drive
3. Plug the USB into your windows laptop
      Ignore issue messegaes and scan to fix
4. Access USB to find two folders:
      Pictures - All saved pictures captured from the camera feeds during inspection with specific filenames to determine their location and status.
      Files - Data logs of files captured to provide evidence of inspections carried out..
5. Once data has been taken (Ensure folders 'Pictures' and 'Files' have not been removed)
6. Re-plug the USB stick drive back into the raspbery pi in the same USB port it was taken out of to begin running code again.
