import cv2
from cv2_enumerate_cameras import enumerate_cameras

def find_camera():
    camera_map = {}
    for camera_info in enumerate_cameras(cv2.CAP_MSMF):
        camera_map[camera_info.name] = camera_info.index

    return camera_map["HD USB Camera"]
    #return camera_map["Logi C615 HD WebCam"]

if __name__ == "__main__":
    print(find_camera())

