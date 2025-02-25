# Plot Figure 6 to 11
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib as mpl

def draw():
    dir_path = "Pic"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


    labelsize = 18
    ticksize = 18
    barwidth = 0.75
    RR = 1.2
    parameters = [
        [5,10,15,20,25,30,35,40,45,50],
        [2,4,6,8,10,12,14,16,18,20],
        [2,4,6,8,10,12,14,16,18,20],
        [2,4,6,8,10,12,14,16,18,20],
        [0.2,0.4,0.6,0.8,1.0,1.2,1.4,1.6,1.8,2.0],
        [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.3,0.45,0.5],
    ]
    R = [0,20,40,60,80,100]
    pos = np.array([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5])


    labels = [r'$N$', r'$Ns$', r'$Nc$', r'$\mathcal{D}$', r'$\nu$', r'$\mu$']
    Labels = ['n', 'ns', 'nc', 'D', 'ee-b', 'tp-b']
    filename = "./output.txt"
    sc = [[],[]]

    for line in open(filename):
        data = line.split()
        if len(data) :
            sc[0].append(float(data[0])*100)
            sc[1].append(float(data[1])*100)

    for i in range(6):
        if i ==4 :
            RR=1.4
        fig, ax1 = plt.subplots(figsize=(8,2.5))
        plt.subplots_adjust(bottom=0.2)
        ax1.set_ylabel('Succ Rate (%)', fontsize=labelsize,labelpad=0)
        ax1.set_ylim(0,RR*R[-1])
        ax1.set_yticks(R)
        ax1.set_yticklabels(R, fontsize=ticksize)
        ax1.set_xlim(0,10)
        ax1.set_xticks(pos)
        ax1.set_xticklabels(parameters[i], fontsize=ticksize)
        ax1.bar(pos - 0.25 * barwidth, sc[0][i*10:(i+1)*10], width = 0.5 * barwidth, color = (247/255, 129/255, 129/255))
        ax1.bar(pos + 0.25 * barwidth, sc[1][i*10:(i+1)*10], width = 0.5 * barwidth, color = (88/255, 172/255, 250/255) )
        ax1.set_xlabel(labels[i], fontsize=16, labelpad=-2)
        ax1.bar(pos - 0.25 * barwidth, sc[0][i*10:(i+1)*10], width=0.5 * barwidth,color=(247/255, 129/255, 129/255), label="Our Method",)
        ax1.bar(pos + 0.25 * barwidth, sc[1][i*10:(i+1)*10], width=0.5 * barwidth,color=(88/255, 172/255, 250/255), label="Baseline Method")
        # ax1.legend(loc='upper right', fontsize=18, ncol=2,frameon=False,prop=font)
        ax1.legend(loc='upper right', ncol=2, frameon=False, prop=font_manager.FontProperties(size=15))

        plt.savefig('./Pic/'+Labels[i]+ '.png',dpi=300)
    avg_sc0 = sum(sc[0]) / len(sc[0])
    avg_sc1 = sum(sc[1]) / len(sc[1])

    print("average(our method) =", avg_sc0)
    print("average(baseline methon) =", avg_sc1)
