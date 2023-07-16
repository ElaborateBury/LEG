import subprocess
import time
import socket
import cv2
import numpy as np

def find_red():
    c = False
    # 定义红色的HSV范围
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    IpLastSegment = "14"
    cam = 2

    udpPORT = [9201, 9202, 9203, 9204, 9205]
    udpSendIntegratedPipe = f"udpsrc address=192.168.123.{IpLastSegment} port={udpPORT[cam - 1]} ! application/x-rtp,media=video,encoding-name=H264 ! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! appsink"

    cap = cv2.VideoCapture()
    cap.open(udpSendIntegratedPipe)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 检查第一行是否存在红色区域
        first_row_mask = mask[0:1, :]
        red_pixels = cv2.countNonZero(first_row_mask)
        if red_pixels > 0:
            c = True
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return c

def get_msg():
    
    
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    
    local_addr = ("0.0.0.0", 8081)
    udp_socket.bind(local_addr)
    while True:
        
        recv_data = udp_socket.recvfrom(1024)
        
        a = recv_data[0].decode('gbk')
        print(a)
        return a
    
    udp_socket.close()


#test_process = subprocess.Popen(["python3", "test.py"])


#test_process.terminate()
#test_process.wait()


#subprocess.call(["python3", "guide.py"])


#test_process = subprocess.Popen(["python3", "test.py"])
if __name__ == '__main__':
  guide_action_count = 0
  test_process = subprocess.Popen(["python3", "test.py"])
  while True:
    b = get_msg()
    if b == "5" and guide_action_count == 0:
      test_process.terminate()
      test_process.wait()
      guide_action_process = subprocess.Popen(["python3", "guide_action.py"])
      time.sleep(10)
      guide_action_process.terminate()
      guide_action_process.wait()
      test_process = subprocess.Popen(["python3", "test.py"])
      guide_action_count +=1
    if b == "2":
      test_process.terminate()
      test_process.wait()
      avoid_process = subprocess.Popen(["python3", "avoid.py"])
      time.sleep(10)
      avoid_process.terminate()
      avoid_process.wait()
      test_process = subprocess.Popen(["python3", "test.py"])
    if b == "1":
      test_process.terminate()
      test_process.wait()
      climb_stairs_process = subprocess.Popen(["python3", "climb_stairs.py"])
      time.sleep(10)
      climb_stairs_process.terminate()
      climb_stairs_process.wait()
      test_process = subprocess.Popen(["python3", "test.py"])
    #c = find_red()
    #if c:
    #  test_process.terminate()
      # test_process.wait()
      # stop_process = subprocess.Popen(["python3", "stop.py"])
      # break
      
    
    