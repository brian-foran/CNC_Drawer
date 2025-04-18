import numpy as np
import cv2
import threading
import time
import os
from find_camera import find_camera

class CameraRecorder:
    def __init__(self, frame_delay=2):
        camera_index = find_camera()
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

        cv2.namedWindow('frame', 0)
        cv2.resizeWindow('frame', 1920, 1080)

        # Check if the camera supports the desired resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if width != 1920 or height != 1080:
            raise Exception(f"Camera does not support resolution 1920x1080, got {width}x{height}")

        # Use H264 codec - revert to XVID if H264 does
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #fourcc = cv2.VideoWriter_fourcc(*'H264')

        self.frame_delay = frame_delay
        self.output_file = 'videos/output.avi'
        self.out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (1920, 1080))
        if not self.out.isOpened():
            raise Exception("Could not open video writer")

        self.thread = threading.Thread(target=self.start_recording)
        self.thread.daemon = True
        self.recording = True
        self.thread.start()

    def start_recording(self):
        while self.cap.isOpened() and self.recording:
            ret, frame = self.cap.read()
            if ret:
                vidout = cv2.resize(frame, (1920, 1080))
                self.out.write(vidout)
                time.sleep(self.frame_delay)
            else:
                break

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.thread.join()
            self.cap.release()
            self.out.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        recorder = CameraRecorder(frame_delay=.5)
        input("Press Enter to stop recording...")
        recorder.stop_recording()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if recorder.cap.isOpened():
            recorder.cap.release()
        if recorder.out.isOpened():
            recorder.out.release()
        cv2.destroyAllWindows()
