import cv2
print(cv2.getBuildInformation())
index = 0
while True:
    cap = cv2.VideoCapture(index)
    if not cap.read()[0]:
        break
    print(f"Camera {index} is available")
    cap.release()
    index += 1
