import cv2
import numpy as np

# 创建空白图像用于显示结果
result = np.zeros((480, 640, 3), dtype=np.uint8)

# 初始化 lower_black 和 upper_black
lower_black = np.array([0, 0, 0], dtype=np.uint8)
upper_black = np.array([180, 255, 30], dtype=np.uint8)


def update_params(lower_black, upper_black):
    # 将帧转换为HSV颜色空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 根据阈值范围创建掩膜
    mask = cv2.inRange(hsv, lower_black, upper_black)

    # 将黑色线提取出来，并将其颜色设为黑色
    result = cv2.bitwise_and(frame, frame, mask=mask)
    result[mask == 0] = [255, 255, 255]  # 将其他颜色设为白色
    result = cv2.dilate(result, None, iterations=10)
    # 显示结果图像
    cv2.imshow("Line Extraction", result)


# 创建回调函数，用于调节参数
def on_trackbar_update(value):
    lower_black[0] = cv2.getTrackbarPos('Hue Lower', 'Trackbars')
    lower_black[1] = cv2.getTrackbarPos('Saturation Lower', 'Trackbars')
    lower_black[2] = cv2.getTrackbarPos('Value Lower', 'Trackbars')
    upper_black[0] = cv2.getTrackbarPos('Hue Upper', 'Trackbars')
    upper_black[1] = cv2.getTrackbarPos('Saturation Upper', 'Trackbars')
    upper_black[2] = cv2.getTrackbarPos('Value Upper', 'Trackbars')

    # 更新参数并显示处理后的图像
    update_params(lower_black, upper_black)


# 创建窗口用于调节参数
cv2.namedWindow('Trackbars')

# 创建滑动条用于调节HSV阈值范围
cv2.createTrackbar('Hue Lower', 'Trackbars', lower_black[0], 180, on_trackbar_update)
cv2.createTrackbar('Saturation Lower', 'Trackbars', lower_black[1], 255, on_trackbar_update)
cv2.createTrackbar('Value Lower', 'Trackbars', lower_black[2], 255, on_trackbar_update)
cv2.createTrackbar('Hue Upper', 'Trackbars', upper_black[0], 180, on_trackbar_update)
cv2.createTrackbar('Saturation Upper', 'Trackbars', upper_black[1], 255, on_trackbar_update)
cv2.createTrackbar('Value Upper', 'Trackbars', upper_black[2], 255, on_trackbar_update)

IpLastSegment = "14"
cam = 2
stop_flag = False
# if len(sys.argv) >= 2:
#    cam = int(sys.argv[1])

# 端口：前方，下巴，左，右，腹部
udpPORT = [9201, 9202, 9203, 9204, 9205]
udpSendIntegratedPipe = f"udpsrc address=192.168.123.{IpLastSegment} port={udpPORT[cam - 1]} ! application/x-rtp,media=video,encoding-name=H264 ! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! appsink"
print("udpSendIntegratedPipe:", udpSendIntegratedPipe)

cap = cv2.VideoCapture(udpSendIntegratedPipe)

while True:
    # 读取相机帧
    ret, frame = cap.read()

    if not ret:
        break

    # 显示原始帧
    cv2.imshow("Original", frame)

    # 更新参数并显示处理后的图像
    update_params(lower_black, upper_black)

    # 按下ESC键退出循环
    if cv2.waitKey(1) == 27:
        break

# 释放相机资源
cap.release()
cv2.destroyAllWindows()
