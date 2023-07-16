import cv2
import numpy as np

# 定义红色的HSV范围
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([179, 255, 255])
IpLastSegment = "14"
cam = 2
stop_flag = False
# if len(sys.argv) >= 2:
#    cam = int(sys.argv[1])

# 端口：前方，下巴，左，右，腹部
udpPORT = [9201, 9202, 9203, 9204, 9205]
udpSendIntegratedPipe = f"udpsrc address=192.168.123.{IpLastSegment} port={udpPORT[cam - 1]} ! application/x-rtp,media=video,encoding-name=H264 ! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! appsink"

# 读取视频流
cap = cv2.VideoCapture(udpSendIntegratedPipe)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 0)
    # 将帧转换为HSV颜色空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 创建红色区域的掩膜
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 进行形态学操作（可选）
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 检查是否存在红色区域
    red_pixels = cv2.countNonZero(mask)
    if red_pixels > 0:
        print("红色区域存在")
    else:
        print("不存在")
    # 显示掩膜和原始帧
    cv2.imshow("Mask", mask)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
