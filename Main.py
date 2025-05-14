import cv2
import os
import threading
import datetime
import queue
import math
import lgpio as GPIO

# Define a global lock for synchronizing access to the cameras
camera_lock = threading.Lock()
frame_queue = queue.Queue()
exit_event = threading.Event()
distance = 0
radius = 50 #radius of the wheel in mm

# Setup GPIO
try:
    h = GPIO.gpiochip_open(0)
    GPIO.gpio_claim_input(h, 11)
except GPIO.error as e:
    print(f"Error: {e}")
    print("Ensure you have the necessary permissions and the GPIO chip is available.")
    exit(1)

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

    def stop(self):
        if self.cam.isOpened():
            self.cam.release()
            print(f"Camera {self.previewName} released")

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
                distance = round(self.count * 2*math.pi*radius*0.0005, 1)
                #print(f"Mock Distance: {distance}m")
                threading.Event().wait(1)  # Simulate delay
            elif GPIO.gpio_read(h, 11) == 1:
                self.count += 1
                distance = round(self.count * 2*math.pi*radius*0.0005, 1)  # Resolution of half a rotation 157mm travel
                #print(f"Distance: {distance}m")
                while GPIO.gpio_read(h, 11) == 1:
                    pass  # Wait for the pin to go low

    def getDistance(self):
        return distance

    def resetDistance(self):
        self.count = 0
        
class BatteryLoggerThread(threading.Thread):
    def __init__(self, log_file_path="/home/pi/battery_life_log.txt"):
        threading.Thread.__init__(self)
        self.log_file_path = log_file_path
        self.running = True

    def run(self):
        print("Starting battery life logger...")
        try:
            with open(self.log_file_path, "a") as file:
                while self.running:
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"{now}\n")
                    file.flush()  # Force write to disk each time
                    print(f"Logged: {now}")
                    time.sleep(60)  # Log every 60 seconds
        except Exception as e:
            print(f"Battery logger error: {e}")

    def stop(self):
        self.running = False

def main():
    chainage = input("Please enter the chainage number you are starting at: ")
    cv2.namedWindow("Left")
    cv2.namedWindow("Right")

    # Position OpenCV windows
    cv2.moveWindow("Left", 0, 0)  # Move "Left" window to top left corner
    cv2.moveWindow("Right", 1280, 0)  # Move "Right" window to top right corner (adjust width as needed)
    
    battery_logger = BatteryLoggerThread()
    battery_logger.start()

    try:
        # Create and start camera threads
        threads = [
            camThread("Left", 0),
            camThread("Right", 2)
        ]

        for thread in threads:
            thread.start()

        # Create and start Hall effect sensor thread
        hall_thread = hallEffectThread(mock_mode=True)
        hall_thread.start()

        print("Active threads:", threading.active_count())

        while not exit_event.is_set():
            if not frame_queue.empty():
                frames = []
                while not frame_queue.empty():
                    frames.append(frame_queue.get())

                for previewName, frame in frames:
                    cv2.imshow(previewName, frame)

            key = cv2.waitKey(20)
            if key in [ord('a'), ord('s'), ord('d'), ord('w')]:
                save_images(key, threads, chainage, hall_thread)
            elif key == ord('c'):
                chainage = input("Please enter new chainage number: ")
                hall_thread.resetDistance()
            elif key == 27:  # ESC to exit
                exit_event.set()

        for thread in threads:
            thread.join()
        hall_thread.join()

    finally:
        for thread in threads:
            if thread.is_alive():
                thread.stop()
        battery_logger.stop()
        battery_logger.join()
        GPIO.gpiochip_close(h)
        cv2.destroyAllWindows()

def save_images(key, threads, chainage, hall_thread):
    """Saves images based on the pressed key."""
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
            path = '/home/rohan/Pictures'
            cv2.imwrite(os.path.join(path, filename), frame_queue.get()[1])
            print(f"Saved {filename}")

if __name__ == "__main__":
    main()