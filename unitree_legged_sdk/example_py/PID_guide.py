import math
import sys
import time
import cv2
import numpy as np


sys.path.append('../lib/python/arm64')
import robot_interface as sdk


def guide_action(a , b ,count ):
    if count == 1:
      HIGHLEVEL = 0xee
      LOWLEVEL = 0xff
      udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.123.161", 8082)
      cmd = sdk.HighCmd()
      state = sdk.HighState()
      udp.InitCmdData(cmd)
      print("000000000000000000")
      cmd.mode = 2
      cmd.bodyHeight = 0
    motiontime = 0
    
    #motiontime = motiontime +1
    
    udp.Recv()
    udp.GetRecv(state)
    #cmd.mode = 0  # 0:idle, default stand      1:forced stand     2:walk continuously
    #cmd.gaitType = 0
    #cmd.speedLevel = 0
    #cmd.footRaiseHeight = 0
    #cmd.bodyHeight = 0
    #cmd.euler = [0, 0, 0]
    #cmd.velocity = [0, 0]
    #cmd.yawSpeed = 0.0
    #cmd.reserve = 0
    print(a,b,count)
      #time.sleep(0.002)
    motiontime +=1
    cmd.mode = 2
    cmd.gaitType = 1
    cmd.bodyHeight = -0.2
            # cmd.position = [1, 0]
            # cmd.position[0] = 2
    cmd.velocity = [0, a]  # -1  ~ +1
    cmd.yawSpeed = 0

    udp.SetSend(cmd)
    udp.Send()
        
def PID_angle(angle_current):
    Kp = 0.015
    Ki = 0.0001
    Kd = 0.001
    target_min = 0
    target_max = 90
    output_min = -5
    output_max = 5

    # ��ʼ������
    previous_error = 0.0
    integral = 0.0

    # �������
    error = abs(target_max) - abs(angle_current)

    # ��������P��
    P = Kp * error

    # ��������I��
    integral += Ki * error
    I = integral

    # ����΢���D��
    derivative = error - previous_error
    D = Kd * derivative
    previous_error = error

    # ���������
    output = P + I + D

    # �����������Χ
    if output > output_max:
        output = output_max
    elif output < output_min:
        output = output_min

    # ��������Ϊ90ʱ��������������Ϊ0
    
    #if abs(angle_current) < 35:
    #    output = 1  
    if angle_current == target_max:
        output = 0
    elif angle_current <0 :
        output = abs(output)
    elif angle_current > 0:
        output = -abs(output)
    if  87 < abs(angle_current) < 90:
        output = 0
    return output


def PID_direction(direction_current):
     # ��ʼ������
    Kp = 0.12 / 800.0  # �����������
    Ki = 0.12 / 100.0  # �����������
    Kd = 0.12 / 1000.0  # ΢���������

    target_min = 110.0
    target_max = 120.0

    # ��ʼ������
    previous_error = 0.0
    integral = 0.0
    # �������
    error = direction_current - ((target_min + target_max) / 2.0)

    # ��������P��
    P = Kp * error

    # ��������I��
    integral += Ki * error
    I = integral

    # ����΢���D��
    derivative = error - previous_error
    D = Kd * derivative
    previous_error = error

    # �����������lateral_speed��
    lateral_speed = P + I + D

    # �����������Χ
    if lateral_speed > 0.03:
        lateral_speed = 0.03
    elif lateral_speed < -0.03:
        lateral_speed = -0.03

    # ���ݷ�������ٶȱ仯��
    if direction_current < target_min:
        lateral_speed -= 0.12 * (130 - direction_current) / 10.0
    elif direction_current > target_max:
        lateral_speed += 0.12 * (direction_current - 140) / 10.0
    
    if lateral_speed > -0.03 and lateral_speed < 0.03:
        lateral_speed = 0
    elif lateral_speed > 0.03:
        lateral_speed = 0.03
    elif lateral_speed < -0.03:
        lateral_speed = -0.03
    if 130 < direction_current < 140:
        lateral_speed = 0
    

    return lateral_speed



