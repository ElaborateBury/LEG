
import sys
import time
import math
import cv2
import numpy as np

sys.path.append('../lib/python/arm64')
import robot_interface as sdk


def guide_action():
    HIGHLEVEL = 0xee
    LOWLEVEL = 0xff
    udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.123.161", 8082)
    cmd = sdk.HighCmd()
    state = sdk.HighState()
    udp.InitCmdData(cmd)
    motiontime = 0
    time.sleep(1)
    motiontime = 1

    udp.Recv()
    udp.GetRecv(state)

        # print(motiontime)
        # print(state.imu.rpy[0])
        # print(motiontime, state.motorState[0].q, state.motorState[1].q, state.motorState[2].q)
        # print(state.imu.rpy[0])

    cmd.mode = 0  # 0:idle, default stand      1:forced stand     2:walk continuously
    cmd.gaitType = 0
    cmd.speedLevel = 0
    cmd.footRaiseHeight = 0
    cmd.bodyHeight = 0
    cmd.euler = [0, 0, 0]
    cmd.velocity = [0, 0]
    cmd.yawSpeed = 0.0
    cmd.reserve = 0
    print(0)
    while motiontime < 100000:
      cmd.mode = 2
      cmd.gaitType = 1
            # cmd.position = [1, 0]
            # cmd.position[0] = 2
      cmd.velocity = [0, 0]  # -1  ~ +1
      cmd.yawSpeed = 0
      cmd.bodyHeight = 0
      
      cmd.euler = [0, -0.3 ,0]
      print(1)
      
      
      
      
      
      
      motiontime+=1
      udp.SetSend(cmd)
      udp.Send()
if __name__ == '__main__':
    guide_action()
