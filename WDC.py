import cv2
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class WDC(object):
    def __init__(self, path2img, step_minute=1, path2test_txt_file=None, path4save='.'):
        self.path = path2img
        self.step = step_minute
        self.test = path2test_txt_file
        self.threshold = (137, 137, 137)
        self.dx = 24*60/564
        self.path2save = path4save
        self.names_of_indexes = ['AU', 'AL', 'AE', 'AO']
        self.dy = {}
        self.interpol = {}

    def read_img(self):
        self.img = cv2.imread(self.path)
        img1, img2 = self.img[26:450 // 2 - 28, 83:-53], self.img[450 // 2 + 29:-54, 81:-53]
        # AU AL AE AO
        self.imgs = \
            img1[: 114 // 2 + 1], img1[114//2+2:], img1[114//2+2:], img2[-30:]

    def coords_from_mask(self, mask):
        x, y = [], []
        for i in range(len(mask[0])):
            for j in range(len(mask)):
                if mask[j][i] == 255:
                    x.append(i);y.append(len(mask)-j)
                    break
        return x, y

    def extract_coordinates(self, ind):
        mask = cv2.inRange(self.imgs[ind], (0, 0, 0), self.threshold)
        x, y, = self.coords_from_mask(mask)
        if ind == 0:
            self.dy[ind] = 1000/len(mask)
            c = 0
        elif ind == 1:
            self.dy[ind] = 2000/len(mask)
            c = -2024
            x, y = [0] + [i * self.dx for i in x] + [1440], [y[0]] + [j * self.dy[ind] + c for j in y] + [
                y[-1] * self.dy[ind] + c]
            return x, y
        elif ind == 2:
            self.dy[ind] = 2000/len(mask)
            c = 20
            y = [len(mask)-j for j in y]

        elif ind == 3:
            self.dy[ind] = 500/len(mask)
            c = -490
        else: return None
        x, y = [0] + [i*self.dx for i in x] + [1440], [y[0]] + [j*self.dy[ind] + c for j in y] + [y[-1]*self.dy[ind]+c]
        return x, y

    def intepolate_by_coords(self, x,y, ind):
        self.interpol[ind] = interpolate.interp1d(x,y)

    def get_values(self, ind):
        minutes = [self.step*i for i in range(int(1440/self.step))]
        values = [self.interpol[ind](minute) for minute in minutes]
        return minutes, values

    def make_plot(self, ind):
        name = self.names_of_indexes[ind]
        minutes, values = self.get_values(ind)
        fig, ax = plt.subplots()
        ax.plot(minutes, values)
        fig.suptitle(name + ' ' + self.path[5:-4], fontsize=20)
        plt.show()

    def interpol_file(self, test):
        if test == None: return None
        txt = open(test).readlines()
        data = []
        for i in range(len(txt)):
            data.append(txt[i].split())
        AU = [int(data[i][-1]) for i in range(len(data))]
        AL = [int(data[i][-2]) for i in range(len(data))]
        AE = [int(data[i][2]) for i in range(len(data))]
        AO = [int(data[i][3]) for i in range(len(data))]
        self.interpol['al_file'] = interpolate.interp1d(range(1441), AL)
        self.interpol['ae_file'] = interpolate.interp1d(range(1441), AE)
        self.interpol['ao_file'] = interpolate.interp1d(range(1441), AO)
        self.interpol['au_file'] = interpolate.interp1d(range(1441), AU)
        
    def plot_test(self):
        if self.test == None: return None
        name = self.names_of_indexes[ind]
        minutes, values = get_values(ind)
        fig, ax = plt.subplots()
        ax.plot(minutes, values)
        ax.plot(test)
        fig.suptitle(name + ' ' + self.path[5:-4], fontsize=20)
        plt.show()

    def mse_test(self):
        deltas = [[] for i in range(4)]
        for i in range(4):
            deltas[i].append(
                self.interpol[i](minute) ** 2 - self.interpol[f"file_{self.names_of_indexes[i]}"](minute) ** 2
            )
        for i in range(4):
            print(self.names_of_indexes[i], deltas[i])
        return deltas

    def write_coords(self, x, y, ind):
        df = pd.DataFrame(data={
            'El': x,
            'y': y
        })
        df.to_csv(self.path2save + f'/coordinates_{self.names_of_indexes[ind]}_{self.path[5:-4]}',
                  index=False)
        return df

