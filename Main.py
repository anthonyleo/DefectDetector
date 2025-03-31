import cv2
import threading
import datetime
import os
import queue

# Define a global lock for synchronizing access to the cameras
camera_lock = threading.Lock()
frame_queue = queue.Queue()
exit_event = threading.Event()

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

def main():
    cv2.namedWindow("Left")
    cv2.namedWindow("Right")

    try:
        # Create and start camera threads
        threads = [
            camThread("Left", 0),
            camThread("Right", 2)
        ]

        for thread in threads:
            thread.start()

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
                save_images(key, threads)
            elif key == 27:  # ESC to exit
                exit_event.set()

        for thread in threads:
            thread.join()

    finally:
        for thread in threads:
            if thread.is_alive():
                thread.stop()
        cv2.destroyAllWindows()

def save_images(key, threads):
    """Saves images based on the pressed key."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
            filename = f"{label}_{thread.previewName}_{timestamp}.jpg"
            path = '/home/rohan/Pictures'
            cv2.imwrite(os.path.join(path, filename), frame_queue.get()[1])
            print(f"Saved {filename}")

if __name__ == "__main__":
    main()