import pandas as pd
import glob
import numpy as np


def check_data(location=r'FiN-Messdaten-LV_Spannung_Teil2'):
    print("Checking location: " + location)
    names = glob.glob(location + "/*.csv")
    print(len(names))
    # df = pd.concat([pd.read_csv(f,header=4,sep = ";",usecols = [0,1,2,3,4,5]) for f in glob.glob(location+"/*.csv")], ignore_index = True)
    # for name in names:
    #    df = pd.read_csv(location+"/tmpFile-1492693540182.csv", header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
    #     df_p1 = df[df['Description']]

    df = pd.read_csv(location + "/tmpFile-1509954126571_incomplete.csv", header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
    df_p1 = df[df['Description'] == "Electric voltage momentary phase 1 (notverified)"]
    df_p2 = df[df['Description'] == "Electric voltage momentary phase 2 (notverified)"]
    df_p3 = df[df['Description'] == "Electric voltage momentary phase 3 (notverified)"]
    print(df_p1.size)
    print(df_p2.size)
    print(df_p3.size)
    print((df_p2.size-df_p1.size)/6)
    print(df.size)


def calculate_meausring_frequency(location=r'FiN-Messdaten-LV_Spannung_Teil2'):
    names = glob.glob(location + "/*.csv")
    table_difference = []
    table_time_avg = []
    table_time_max = []
    df = pd.read_csv(location + "/tmpFile-1492693540182.csv", header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
    df_p1 = df[df['Description'] == "Electric voltage momentary phase 1 (notverified)"].reset_index()
    df_p2 = df[df['Description'] == "Electric voltage momentary phase 2 (notverified)"].reset_index()
    df_p3 = df[df['Description'] == "Electric voltage momentary phase 3 (notverified)"].reset_index()
    times1 = pd.to_datetime(df_p1.loc[:, "TimeStamp"])
    times2 = pd.to_datetime(df_p2.loc[:, "TimeStamp"])
    times3 = pd.to_datetime(df_p3.loc[:, "TimeStamp"])
    print(times1)
    print(times2)
    differences = []
    for t in range(1, times1.size):
        if (times1[t-1] - times1[t]).total_seconds() <0:
            print("{}:{}",t,(times1[t-1] - times1[t]).total_seconds())
        differences.append((times1[t-1] - times1[t]).total_seconds())
    print(differences)
    print(list(filter(lambda x: x > 60, differences)))
    print(list(filter(lambda x: x < 8, differences)))
    print(np.average(differences))
    print(np.amax(differences))


def unique_series(location=r'FiN-Messdaten-LV_Spannung_Teil2'):
    df = pd.read_csv(location + "/tmpFile-1492693540182.csv", header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
    df_p1 = df[df['Description'] == "Electric voltage momentary phase 1 (notverified)"]
    times1 = pd.to_datetime(df_p1.loc[:, "TimeStamp"])
    differences = []
    x = 0
    for t in range(1, times1.size):
        if (times1[t-1] - times1[t]).total_seconds() <10:
            x = t
            print("{}:{}",t,(times1[t-1] - times1[t]).total_seconds())
        differences.append((times1[t-1] - times1[t]).total_seconds())
    series = df.loc[:, "AliasName"].first(x)
    print(len(series.unique()))

def main():
    print("Starting")
    # calculate_meausring_frequency()
    unique_series()

main()
