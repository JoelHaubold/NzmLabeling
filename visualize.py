import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import os
import time
import numpy


def plot_sdp(sdp_name, l_width, picture_number, df):
    print("ctime: " + str(time.time() - start))
    pos1 = df.Description == 'Electric voltage momentary phase 1 (notverified)'
    df_phase1 = df.loc[pos1, :]
    pos2 = df.Description == 'Electric voltage momentary phase 2 (notverified)'
    df_phase2 = df.loc[pos2, :]
    pos3 = df.Description == 'Electric voltage momentary phase 3 (notverified)'
    df_phase3 = df.loc[pos3, :]
    # dfV1 = df.Value.astype(float)
    # plot mit pandas
    print("time: " + str(time.time() - start))
    plt.rcParams['figure.dpi'] = 200

    plt.figure(2)
    plt.ylabel('Phases')
    df_phase1.Value.plot(figsize=(24, 6), linewidth=l_width, label='Phase1')
    df_phase2.Value.plot(figsize=(24, 6), linewidth=l_width, label='Phase2')
    df_phase3.Value.plot(figsize=(24, 6), linewidth=l_width, label='Phase3')
    legend = plt.legend(fontsize='x-large', loc='lower left')

    for line in legend.get_lines():
        line.set_linewidth(4.0)

    pictureName = str(picture_number) + 'Overlap'
    plotPath = r'/home/joelhaubold/Dokumente/BADaten/Plots/'+ sdp_name
    if not os.path.exists(plotPath):
        os.makedirs(plotPath)
    plt.savefig(plotPath + "/" + picture_number)
    plt.close(2)


def plot(new_path, l_width, picture_number):
    df = pd.read_csv(new_path, header=4, sep=';', usecols=[0, 1, 2, 3, 4, 5], decimal=",")
    df = df.set_index('TimeStamp')
    df = df.sort_index()

    sdp_list = df.ServiceDeliveryPoint.unique()
    print(sdp_list)
    for sdp in sdp_list:
        df_sdp = df.loc[df.ServiceDeliveryPoint == sdp, :]
        plot_sdp(sdp, l_width, picture_number, df_sdp)


def plot_single(path):
    number = Path(path).stem
    plot(path, 1.2, number)


def plot_all(directory_path):
    file_paths = os.listdir(directory_path)
    for path in file_paths:
        number = Path(path).stem
        print(number)
        plot(directory_path+"/"+path, 1.2, number)


def plot_pickel_data(plot_directory, df_phases):
    l_width = 1.2

    plt.rcParams['figure.dpi'] = 200
    df_p1 = df_phases['Phase1']
    min = pd.to_datetime(df_p1.index.to_series()).min()
    max = pd.to_datetime(df_p1.index.to_series()).max()
    nmbr_days = (max-min)/numpy.timedelta64(1,"D")
    nmbr_days = int(numpy.ceil(nmbr_days))
    print(nmbr_days)
    nmbr_days = 10
    for d in range(1, nmbr_days):
        for key, value in df_phases.items():
            timeStamps = pd.to_datetime(value.index.to_series())
            print(timeStamps)
            min_p = timeStamps.min
            day = numpy.timedelta64(1, "D")
            # df_day = value.loc[min_p + day * (d - 1): min_p + day * d]
            df_day = value.loc[1: 5]
            df_phases[key] = df_day
        plt.figure(d)
        plt.ylabel('Phases')
        for key, value in df_phases.items():
            value.Value.plot(figsize=(24, 6), linewidth=l_width, label=key)
            # df_phase2.Value.plot(figsize=(24, 6), linewidth=l_width, label='Phase2')
        legend = plt.legend(fontsize='x-large', loc='lower left')

        for line in legend.get_lines():
            line.set_linewidth(4.0)

        plotPath = plot_directory
        if not os.path.exists(plotPath):
            os.makedirs(plotPath)
        plt.savefig(plotPath + "/" + d)
        plt.close(d)


def plot_pickle(pickle_directory):
    df = pd.read_pickle(pickle_directory+"/3PhasesDF")
    print(df)
    pos1 = df.Description == 'Electric voltage momentary phase 1 (notverified)'
    df_phase1 = df.loc[pos1, :]
    pos2 = df.Description == 'Electric voltage momentary phase 2 (notverified)'
    df_phase2 = df.loc[pos2, :]
    pos3 = df.Description == 'Electric voltage momentary phase 3 (notverified)'
    df_phase3 = df.loc[pos3, :]
    for df_p in [df_phase1]:
        difs = df_p.Value.diff()
        print(difs)
    df = pd.concat([df_phase1,df_phase2,df_phase3])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    print(df)
    day = pd.Timedelta('1d')
    min = pd.to_datetime(df.index.to_series()).min()
    max = pd.to_datetime(df.index.to_series()).max()
    nmbr_days = (max - min) / day
    nmbr_days = int(numpy.ceil(nmbr_days))
    print(nmbr_days)
    nmbr_days = 10
    for start_time in pd.date_range(min, max, freq='d'):
        end_time = start_time + day
        #df_day = df.loc[df.index>start_time and df.index<end_time, :]
        df_day = df.loc[start_time:end_time]
        print(df_day)
    #plot_pickel_data(r"/home/joelhaubold/Dokumente/BADaten/Plots/PicklePlots", {'Phase1':df_phase1, 'Phase2':df_phase2, 'Phase3':df_phase3}) TODO


def main():
    path = r'/home/joelhaubold/Dokumente/BADaten/FiN-Messdaten-LV_Spannung_Teil2/tmpFile-1508483157110.csv'
    # directory_path = r'/home/joelhaubold/Dokumente/BADaten/FiN-Messdaten-LV_Spannung_Teil2'
    plot_pickle("pickles/NW00000000000BISMARKSTRASSNV00595")


start = time.time()
main()
end = time.time()
print("time: " + str(end - start))