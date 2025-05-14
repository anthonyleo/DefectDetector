import cv2
import os
import threading
import datetime
import queue
import math
from gpiozero import Button

# Define a global lock for synchronizing access to the cameras
camera_lock = threading.Lock()
frame_queue = queue.Queue()
exit_event = threading.Event()
distance = 0
radius = 50  # radius of the wheel in mm
magNum = 2  # number of magnets on the wheel
hallEffectSig = 17  # GPIO pin for Hall effect sensor

# Initialize the Hall effect sensor
hall_sensor = Button(hallEffectSig)

class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
        self.cam = cv2.VideoCapture(camID)

        if not self.cam.isOpened():
            print(f"Error: Unable to open camera {previewName}")

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cam.set(cv2.CAP_PROP_FPS, 10)

    def run(self):
        print(f"Starting {self.previewName}")
        while not exit_event.is_set():
            with camera_lock:  # Acquire the lock to access the camera
                rval, frame = self.cam.read()

            if not rval:
                print(f"Error: Unable to grab frame from camera {self.previewName}")
                break

            frame_queue.put((self.previewName, frame))

        self.cam.release()
        print(f"Camera {self.previewName} released in run()")

    def stop(self):
        if self.cam.isOpened():
            self.cam.release()
            print(f"Camera {self.previewName} released in stop()")

class hallEffectThread(threading.Thread):
    def __init__(self, mock_mode=False):
        threading.Thread.__init__(self)
        self.count = 0
        self.mock_mode = mock_mode

    def run(self):
        global distance
        while not exit_event.is_set():
            if self.mock_mode:
                # Simulate the Hall effect sensor
                self.count += 1
                distance = round(self.count * 2 * math.pi * radius * 0.001 * (1 / magNum), 1)
                threading.Event().wait(1)  # Simulate delay
            else:
                if hall_sensor.is_pressed:
                    self.count += 1
                    distance = round(self.count * 2 * math.pi * radius * 0.001 * (1 / magNum), 1)
                    #print(f"Distance: {distance}m")
                    while hall_sensor.is_pressed:
                        pass  # Wait for the pin to go low

    def getDistance(self):
        return distance

    def resetDistance(self):
        global distance
        self.count = 0
        distance = 0

def main():
    chainage = input("Please enter the chainage number you are starting at: ")
    cv2.namedWindow("Left")
    cv2.namedWindow("Right")

    # Position OpenCV windows
    cv2.moveWindow("Left", 0, 0)  # Move "Left" window to top left corner
    cv2.moveWindow("Right", 1280, 0)  # Move "Right" window to top right corner (adjust width as needed)

    # Create the text file with the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    txt_filename = f"data-{timestamp}.txt"
    txt_filepath = os.path.join('/media/rohan/6790-17CB/Files', txt_filename)

    try:
        # Create and start camera threads
        threads = [
            camThread("Left", 0),
            camThread("Right", 2)
        ]

        for thread in threads:
            thread.start()

        # Create and start Hall effect sensor thread
        hall_thread = hallEffectThread(mock_mode=False)
        hall_thread.start()

        # Reset distance after initializing the Hall effect sensor
        hall_thread.resetDistance()

        print("Active threads:", threading.active_count())

        while not exit_event.is_set():
            if not frame_queue.empty():
                frames = []
                while not frame_queue.empty():
                    frames.append(frame_queue.get())

                for previewName, frame in frames:
                    cv2.imshow(previewName, frame)

            key = cv2.waitKey(20) & 0xFF
            if key in [ord('a'), ord('s'), ord('d'), ord('w')]:
                save_images(key, threads, chainage, hall_thread, txt_filepath)
            elif key == ord('c'):
                chainage = input("Please enter new chainage number: ")
                hall_thread.resetDistance()
            elif key == 27:  # ESC to exit
                print("ESC key pressed. Exiting...")
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        print("Stopping all threads...")

        exit_event.set()  # Signal all threads to exit

        for thread in threads:
            if thread.is_alive():
                thread.stop()
                thread.join(timeout=5)  # Add timeout to prevent indefinite blocking

        hall_thread.join(timeout=5)  # Add timeout to prevent indefinite blocking
        hall_sensor.close()  # Properly close the Hall effect sensor

        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Ensure all windows are closed
        print("All windows destroyed") #Here

def save_images(key, threads, chainage, hall_thread, txt_filepath):
    """Saves images based on the pressed key and logs the filename to a text file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    for thread in threads:
        if key == ord('a'):
            label = "Defect" if thread.previewName == "Left" else "OK"
        elif key == ord('s'):
            label = "Defect"
        elif key == ord('d'):
            label = "OK" if thread.previewName == "Left" else "Defect"
        elif key == ord('w'):
            label = "OK"

        if label:
            filename = f"{label}_{thread.previewName}_{hall_thread.getDistance()}m from chain {chainage}_{timestamp}.jpg"
            path = '/media/rohan/6790-17CB/Pictures'
            cv2.imwrite(os.path.join(path, filename), frame_queue.get()[1])
            print(f"Saved {filename}")

            # Append the filename to the text file
            with open(txt_filepath, 'a') as f:
                f.write(f"{filename}\n")

if __name__ == "__main__":
    main()