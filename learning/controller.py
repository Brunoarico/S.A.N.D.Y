from myo_raw import *
import socket
import enum
from playsound import playsound
from threading import Thread

class Arm_Pose(enum.Enum):
    ARM_NONE = -1
    ARM_UP = 0
    ARM_MID = 1
    ARM_DOWN = 2

class Hand_Pose(enum.Enum):
    FACE_HAND_NONE = -1
    FACE_HAND_UP = 0
    FACE_HAND_MID = 1
    FACE_HAND_DOWN = 2


class Controller():
    def __init__(self):
        self.myo = MyoRaw()
        self.host = "192.168.0.199"
        self.port = 80
        self.hand_state = Hand_Pose.FACE_HAND_NONE
        self.arm_state = Arm_Pose.ARM_NONE
        self.pose_state = Pose.REST
        self.myo.connect()
        self.myo.add_imu_handler(self.IMU_get)
        self.myo.add_pose_handler(self.state_machine)

    def IMU_get(self, euler, acc, gyro):
        #euler[2] face palm
        if(45 < int(euler[2]) < 80):
            #print("HAND UP")
            self.hand_state = Hand_Pose.FACE_HAND_UP
        elif(15<int(euler[2]) < 45):
            #print("HAND MID")
            self.hand_state = Hand_Pose.FACE_HAND_MID
        elif int(-80<int(euler[2])<15):
            #print("HAND DOWN")
            self.hand_state = Hand_Pose.FACE_HAND_DOWN
        else:
            #print("HAND NONE")
            self.hand_state = Hand_Pose.FACE_HAND_NONE

        #euler[1] arm vertical
        if(25 < int(euler[1]) < 90):
            #print("ARM DOWN")
            self.arm_state = Arm_Pose.ARM_DOWN

        elif(-25 <int(euler[1]) < 25):
            #print("ARM MID")
            self.arm_state = Arm_Pose.ARM_MID
        elif(-90<int(euler[1])<-24):
            #print("ARM UP")
            self.arm_state = Arm_Pose.ARM_UP
        else:
            #print("ARM NONE")
            self.arm_state = Arm_Pose.ARM_NONE
        #print(int(euler[0]), int(euler[1]), int(euler[2]))

    def send(self, msg):
        sock = socket.socket()
        sock.connect((self.host, self.port))
        sock.send(msg.encode())
        print(msg)

    def state_machine(self, p):
        self.pose_state = p

        if(self.arm_state == Arm_Pose.ARM_UP):
            if(self.pose_state == Pose.THUMB_TO_PINKY):
                if(self.hand_state ==Hand_Pose.FACE_HAND_DOWN):
                    message = "LED161 "
                    self.send(message)
                if(self.hand_state ==Hand_Pose.FACE_HAND_UP):
                    message = "LED051 "
                    self.send(message)


        if(self.arm_state == Arm_Pose.ARM_DOWN):
            if(self.pose_state == Pose.THUMB_TO_PINKY):
                if(self.hand_state ==Hand_Pose.FACE_HAND_DOWN):
                    message = "LED160 "
                    self.send(message)
                if(self.hand_state ==Hand_Pose.FACE_HAND_UP):
                    message = "LED050 "
                    self.send(message)

        if(self.arm_state == Arm_Pose.ARM_MID):
            print(self.pose_state)
            if(self.pose_state == Pose.WAVE_OUT):
                print("Pew UP")
                Thread(target=playsound("/home/aviador/Documents/Projects/Myo_control/learning/sounds/PWRUP1.wav")).start() # create thread
                print("ok")

            elif(self.pose_state == Pose.FIST):
                print("Pew DOWN")
                Thread(target=playsound("/home/aviador/Documents/Projects/Myo_control/learning/sounds/PWRDOWN1.wav")).start() # create thread
                print("ok")
    def run(self):

        try:
            while True:
                self.myo.run(1)

        except KeyboardInterrupt:
            pass
        finally:
            self.myo.disconnect()
            print()

c = Controller()
c.run()
