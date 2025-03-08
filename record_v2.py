import numpy as np
import cv2
import threading
import time
import os
from find_camera import find_camera

class CameraRecorder:
    def __init__(self):
        camera_index = find_camera()
        self.cap = cv2.VideoCapture(camera_index)
        cv2.namedWindow('frame', 0)
        cv2.resizeWindow('frame', 1920, 1080)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self.output_file = 'videos/output.avi'
        self.out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (1920, 1080))
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
                time.sleep(2)
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
    recorder = CameraRecorder()
    input("Press Enter to stop recording...")
    recorder.stop_recording()
    if recorder.cap.isOpened():
        recorder.cap.release()
    if recorder.out.isOpened():
        recorder.out.release()
    cv2.destroyAllWindows()
