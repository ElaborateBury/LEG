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
    time.sleep(0.002)
    motiontime = 0

    udp.Recv()
    udp.GetRecv(state)
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
    while True:
      if (motiontime<=20000):
        cmd.mode = 2
        cmd.gaitType = 1
        cmd.velocity = [0.8, 0.12]  # -1  ~ +1
        cmd.yawSpeed = 0
        cmd.bodyHeight = 0
      if (20001<=motiontime<=80000):
        cmd.mode = 2
        cmd.gaitType = 1
        cmd.velocity = [0, 0]  # -1  ~ +1
        cmd.yawSpeed = 0.5
        cmd.bodyHeight = 0 
      if (80001<=motiontime<=108000):
        cmd.mode = 2
        cmd.gaitType = 1
        cmd.velocity = [0.8, 0]  # -1  ~ +1
        cmd.yawSpeed = 0
        cmd.bodyHeight = 0 
      if (108001<=motiontime<=160000):
        cmd.mode = 2
        cmd.gaitType = 1
        cmd.velocity = [0, 0]  # -1  ~ +1
        cmd.yawSpeed = -0.5
        cmd.bodyHeight = 0 
      if (163001<=motiontime<=178000):
        cmd.mode = 2
        cmd.gaitType = 1
        cmd.velocity = [0.8, 0]  # -1  ~ +1
        cmd.yawSpeed = 0
        cmd.bodyHeight = 0
      if (178001<=motiontime<=180000):
        cmd.mode = 2
        cmd.gaitType = 1
        cmd.velocity = [0, 0]  # -1  ~ +1
        cmd.yawSpeed = 0
        cmd.bodyHeight = 0
      if (motiontime >178000):
        break
      print(motiontime)
      motiontime += 1
      udp.SetSend(cmd)
      udp.Send()
if __name__ == '__main__':
    guide_action()
