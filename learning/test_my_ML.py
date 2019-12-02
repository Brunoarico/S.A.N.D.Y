from collections import Counter, deque
import sys
import time
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import pygame
from pygame.locals import *

from common import *
from myo_raw import MyoRaw



w, h = 800, 320

N = 10
K = 15
SUBSAMPLE = 3

class MyoClassifier():
    def __init__(self, gyro = True):
        self.Gyro = gyro
        if(self.Gyro):
            self.columns = ['EMG_1','EMG_2','EMG_3','EMG_4','EMG_5','EMG_6','EMG_7','EMG_8','P_1','P_2','P_3', 'Class']
        else:
            self.columns = ['EMG_1','EMG_2','EMG_3','EMG_4','EMG_5','EMG_6','EMG_7','EMG_8', 'Class']
        self.data = pd.DataFrame(columns=self.columns)
        self.emg = None
        self.imu = None
        self.y = None
        self.counter = 0
        self.m = MyoRaw()
        self.H_count = [0]*N

    def emg_handler(self, emg, moving):
        self.emg = emg

    def imu_handler(self, euler, acc, gyro):
        self.imu = [int(euler[0]), int(euler[1]), int(euler[2])]

    def store_data(self):
        if(((not self.imu == None) or not self.Gyro) and (not self.emg == None)):
            if(self.Gyro):
                v = list(self.emg) + self.imu + [self.y]
            else:
                v = list(self.emg) + [self.y]
            print(v)
            self.imu = None
            self.emg = None
            self.data.loc[self.counter] = v
            self.counter += 1
            self.H_count[self.y] += 1
            #print(self.data)
            self.train()

    def train(self):
        if(self.counter > SUBSAMPLE * K):
            X = self.data.drop(columns=['Class'])
            y = self.data['Class'].values.astype('int')
            #print(y)
            self.nn = KNeighborsClassifier(n_neighbors=K, algorithm='kd_tree')
            #X_train, self.X_test, y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=1, stratify=y)
            #print(self.X_test)
            self.nn.fit(X, y)
            print("trained")

    def test(self):
        if(self.counter > SUBSAMPLE * K):
            if(((not self.imu == None) or not self.Gyro) and (not self.emg == None)):
                if(self.Gyro):
                    v = list(self.emg) + self.imu
                else:
                    v = list(self.emg)
                tdata = pd.DataFrame(columns=self.columns)
                tdata = tdata.drop(columns=['Class'])
                tdata.loc[0] = v
                #print(tdata.iloc[[0]])
                print("Predict:", self.nn.predict(tdata.iloc[[0]]))

    def run_learned(self, name):
        self.counter = 1000
        df = pd.read_csv(name, index_col=0)
        X = df.drop(columns=['Class'])
        y = df['Class'].values.astype('int')
        self.nn = KNeighborsClassifier(n_neighbors = K, algorithm='kd_tree')
        self.nn.fit(X, y)
        self.m.add_emg_handler(self.emg_handler)
        self.m.add_imu_handler(self.imu_handler)                                                                              #<<<<<<<<<<<<<<<<
        self.m.connect()
        while True:
            self.m.run()
            self.test()


    def run_learning(self, name):
        pygame.init()
        scr = pygame.display.set_mode((w, h))
        font = pygame.font.Font(None, 30)
        self.m.add_emg_handler(self.emg_handler)
        self.m.add_imu_handler(self.imu_handler)                                                                              #<<<<<<<<<<<<<<<<
        self.m.connect()
        try:
            r = 0
            while True:
                self.m.run()

                for ev in pygame.event.get():
                    if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                        raise KeyboardInterrupt()

                    elif ev.type == KEYDOWN:
                        if K_0 <= ev.key <= K_9: #THIS
                            self.y = ev.key - K_0

                        elif ev.key == K_SPACE:
                            print("test")
                            self.test()

                    elif ev.type == KEYUP:
                        if K_0 <= ev.key <= K_9:
                            self.y = None



                if(not (self.y == None)):
                    self.store_data()


                scr.fill((0, 0, 0), (0, 0, w, h))

                for i in range(N):
                    x = 0
                    y = 0 + 30 * i

                    clr = (0,200,0) if i == r else (255,255,255)

                    txt = font.render('%5d' % self.H_count[i], True, (255,255,255))
                    scr.blit(txt, (x + 20, y))

                    txt = font.render('%d' % i, True, clr)
                    scr.blit(txt, (x + 110, y))

                    #scr.fill((0,0,0), (x+130, y + txt.get_height() / 2 - 10, len(m.history) * 20, 20))
                    #scr.fill(clr, (x+130, y + txt.get_height() / 2 - 10, m.history_cnt[i] * 20, 20))

                pygame.display.flip()

        except KeyboardInterrupt:
                pass
        finally:
                self.m.disconnect()
                self.data.to_csv(name)
                pygame.quit()
                print()

if __name__ == '__main__':
    mc = MyoClassifier(gyro = False)

    if(len(sys.argv) > 1):
        name = sys.argv[1]+".csv"
        try:
            open(name)
            print("Reading File...")
            mc.run_learned(name)
        except FileNotFoundError:
            print("Creating a File...")
            mc.run_learning(name)
