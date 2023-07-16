import math
import sys
import cv2
import numpy
import numpy as np
import time
from PID_guide import PID_angle, PID_direction
import threading
import subprocess

sys.path.append('../lib/python/arm64')
import robot_interface as sdk

yawspeed_share = 0
velocity_share = 0
stop_share = True
lock = threading.Lock()
stop_event = threading.Event()
restart_count = 0

def find_line():
    global yawspeed_share
    global velocity_share
    global restart_count
    global c_share
    count = 0
    pre_angle = 0
    cur_angle = 0
    error = 0
    try:
        if count < 1:
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

            # while True:
            #     if cap.isOpened()==False:
            #         print('cam not open camrea')
            #         break
            #     ret, frame = cap.read()
            #     if ret == False:
            #         continue
            #
            #     cv2.namedWindow('frame')
            #     cv2.imshow('frame',frame)
            #
            #     mykey=cv2.waitKey(1)
            #
            #     if mykey & 0xFF == ord('q'):
            #         break

            # cap.release()
            # cv2.destroyAllWindows()
            # cap = cv2.VideoCapture(0)
            ERROR = -999
            run_flag = 0  # 通过该标志位用来在识别到黑色十字之后停止
            # center定义
            center = 321

        while (1):
            c = 0.12
            ret, frame = cap.read()
            frame = cv2.flip(frame, 0)
            if np.all(frame[0] == [0, 0, 255]):  # Check if the first row is red
              restart_count = 10
              stop_event.set()  # Signal other threads to stop
              subprocess.run(["python", "stop.py"])  # Run stop.py file
              break  # Exit the loop and terminate the program

            # 转化为灰度图
            if ret == False:  # 如果是最后一帧这个值为False
                break
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # 大津法二值化
            #retval, dst = cv2.threshold(gray, 100, 255, cv2.THRESH_OTSU)
            
            lower_black = np.array([0, 0, 0], dtype=np.uint8)
            upper_black = np.array([180, 255, 80], dtype=np.uint8)
            
            
            
            # # 腐蚀，白区域变小
            # dst = cv2.erode(dst, None, iterations=6)
            dst = cv2.inRange(hsv, lower_black, upper_black)
            dst = cv2.bitwise_not(dst)
            # 膨胀，白区域变大
            dst = cv2.dilate(dst, None, iterations=3)
            cv2.imshow("dst", dst)
            
            # 看第400行的像素值，第400行像素就约等与图片的底部
            color = dst[400]
            # 再看第200行的像素值与第300行的像素值
            color1 = dst[200]
            color2 = dst[300]
            color3 = dst[1]
            # 找到黑色的像素点个数
            black_count = np.sum(color ==0)
            print("黑色像素点为：", black_count)
            if black_count >= 1000:  # 假如识别到了黑色十字就给串口发r:0000l:0000让小车停下来
                time.sleep(0.2)
                # ser.write("r:0000l:0000\r\n".encode())
                run_flag = 1
            else:
                run_flag = 0  # 未识别到黑色十字
            # 找到黑色的像素点索引
            if np.sum(color3 == 255) == 0:
                c = -0.01
            else:
                c = 0.12 
            black_count_judge = np.sum(color == 255)  # 利用这个变量来查找摄像头是否观察到黑色
            if black_count_judge == 640:
                print("黑色像素点为:0")
                time.sleep(0.2)
                # ser.write("r:0000l:0000\r\n".encode())  # 在这里我加上了串口
                pass
            else:
                if run_flag == 0:
                    black_index = np.where(color == 0)
                    # 防止black_count=0的报错
                    if black_count == 0:
                        black_count = 1
                    # 在这里，我们要计算偏移的角度。
                    black_count1_judge = np.sum(color1 == 255)  # 第200行如果全是白色的话就不计算角度了
                    black_count2_judge = np.sum(color2 == 255)
                    black_index1 = np.where(color1 == 0)
                    black_index2 = np.where(color2 == 0)
                    black_count1 = np.sum(color1 == 0)
                    black_count2 = np.sum(color2 == 0)
                    if black_count1_judge < 9999 and black_count2_judge < 9999:
                        if black_count1 == 0:
                            stop_share = False
                        center1 = (black_index1[0][black_count1 - 1] + black_index1[0][0]) / 2  # 对应的是第200行
                        direction1 = center1 - 302
                        center2 = (black_index2[0][black_count2 - 1] + black_index2[0][0]) / 2  # 对应的是第300行
                        direction2 = center2 - 302
                        print("center1:", center1, "center2:", center2)
                        angle = '%.2f' % (math.degrees(numpy.arctan(100 / (direction2 - direction1))))
                        print("偏转角为：", angle)
                        cv2.line(frame, (int(center2), 300), (int(center1), 200), color=(255, 0, 0), thickness=3)  # 蓝色的线
                        cv2.line(frame, (0, 300), (940, 300), color=(0, 0, 255), thickness=3)  # 红色的线
                        cv2.line(frame, (0, 200), (940, 200), color=(0, 0, 255), thickness=3)
                        cv2.imshow("frame", frame)
                        pass
                    if black_count1_judge >= 9999 or black_count2_judge >= 9999:  # 如果没有发现第150行喝第300行的黑线
                        angle = ERROR
                        print("偏转角为：", angle)
                        pass
                    # 找到黑色像素的中心点位置
                    center = (black_index[0][black_count - 1] + black_index[0][0]) / 2
                    direction = center - 302  # 在实际操作中，我发现当黑线处于小车车体正中央的时候应该减去302
                    direction = int('%4d' % direction)
                    print("方向为：", direction)
                    # 计算出center与标准中心点的偏移量
                    '''当黑线处于小车车体右侧的时候，偏移量为正值，黑线处于小车车体左侧的时候，偏移量为负值（处于小车视角）'''
                    # if direction > 0:
                    #     right_param = 1999 + (direction * 4)  # 这个参数可以后期更改
                    #     light_param = 1999
                    #     final_param = 'r:' + str(light_param) + 'l:' + str(right_param) + '\r\n'
                    #     print(final_param)
                    #     time.sleep(0.2)
                    #     # ser.write(final_param.encode())
                    #     c,d = PID(direction,angle)
                    #
                    #
                    # else:
                    #     media = -direction
                    #     light_param = 1999 + (media * 4)
                    #     right_param = 1999
                    #     final_param = 'r:' + str(light_param) + 'l:' + str(right_param) + '\r\n'
                    #     print(final_param)
                    #     time.sleep(0.2)
                    #     # ser.write(final_param.encode())

                    velocity = PID_direction(direction)
                    yawspeed = PID_angle(float(angle))


                    # if count % 2 == 0:
                    #     cur_angle = abs(float(angle))
                    # else:
                    #     pre_angle = cur_angle
                    #     cur_angle = abs(float(angle))
                    # if count >= 1:
                    #     error = abs(abs(pre_angle) - abs(cur_angle))
                    # count = count + 1

                    if np.sum(color3 == 255) == 640:
                        if abs(float(angle)) < 40:
                            yawspeed = 0
                        else:
                            if np.sum(color3 == 0) == 640:
                                c = -0.01
                            
                    else:
                        if abs(float(angle)) < 40:
                            c = -0.01
                        else:
                            c = 0.12
                    if np.sum(color3 == 0) == 640:
                        c = -0.01

                    # if error > 45:
                    #     c = -0.12
                    # else:
                    #     c = 0.12
                    # if np.sum(color3 == 255) == 640:
                    #     yawspeed = 0
                    #     c = 0.12


                    # if np.sum(color3 == 0) == 640 or np.sum(color3 == 255) > 320:
                    #     if abs(float(angle)) < 30:
                    #         yawspeed = 0
                    # else:
                    #     if abs(float(angle)) < 35 or np.sum(color3 == 0) > 520:
                    #         c = -0.01
                    #     else:
                    #         c = 0.12

                    with lock:
                        velocity_share = velocity
                        yawspeed_share = yawspeed
                        c_share = c
                else:
                    print("小车已经停止\n")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        restart_count += 1
        print("find_line error:", e)
        stop_event.set()
    # 释放清理
    finally:
        cap.release()
        cv2.destroyAllWindows()


def guide_action():
    global yawspeed_share
    global velocity_share
    global c_share
    global restart_count
    HIGHLEVEL = 0xee
    LOWLEVEL = 0xff
    udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.123.161", 8082)
    cmd = sdk.HighCmd()
    state = sdk.HighState()
    udp.InitCmdData(cmd)
    motiontime = 0

    # motiontime = motiontime +1
    try:
        while True:
            if stop_event.is_set():
              break 
            with lock:
                velocity_share_send = velocity_share
                yawspeed_share_send = yawspeed_share
                c_send = c_share
            udp.Recv()
            udp.GetRecv(state)
            # cmd.mode = 0  # 0:idle, default stand      1:forced stand     2:walk continuously
            # cmd.gaitType = 0
            # cmd.speedLevel = 0
            # cmd.footRaiseHeight = 0
            # cmd.bodyHeight = 0
            # cmd.euler = [0, 0, 0]
            # cmd.velocity = [0, 0]
            # cmd.yawSpeed = 0.0
            # cmd.reserve = 0
            # time.sleep(0.002)
            motiontime += 1
            cmd.mode = 2
            cmd.gaitType = 1
            # cmd.position = [1, 0]
            # cmd.position[0] = 2
            cmd.velocity = [c_send, velocity_share_send]  # -1  ~ +1
            cmd.yawSpeed = yawspeed_share_send
            cmd.bodyHeight = -0.3
            udp.SetSend(cmd)
            udp.Send()
            time.sleep(0.01)
    except Exception as e:
        restart_count += 1
        print("guide_action error:", e)


if __name__ == '__main__':
    # find_line_thread = threading.Thread(target=find_line)
    # guide_action_thread = threading.Thread(target=guide_action)
    # find_line_thread.start()
    # time.sleep(4.5)
    # guide_action_thread.start()

    # find_line_thread.join()
    # guide_action_thread.join()
    counter = 0
    while restart_count < 10:
        try:
            stop_event.clear() 
            find_line_thread = threading.Thread(target=find_line)
            guide_action_thread = threading.Thread(target=guide_action)
            find_line_thread.start()
            time.sleep(4.5)
            guide_action_thread.start()
            
            
            find_line_thread.join()
            guide_action_thread.join()

        except Exception as e:
            print(f"Error in threads: {e}, Restarting...")
            stop_event.set()  # Signal other threads to stop
            find_line_thread.join()  # If an exception occurred, stop the threads
            guide_action_thread.join()
            continue
    print("Maximum restart count reached. Exiting...")
