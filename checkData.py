import pandas as pd
import glob

import numpy as np


def is_part_of_df(location1, location2):
    names = glob.glob(location1 + "/*.csv")
    unequal_files = []
    for name in names:
        file_name = name.split(location1)[-1]
        df1 = pd.read_csv(name, header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
        df2 = pd.read_csv(location2+file_name, header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
        if not df1.equals(df2) :
            unequal_files.append(file_name)
        # print("{} / {}".format(names.index(name), len(names)))
    return unequal_files

def calculate_meausring_frequency(location=r'FiN-Messdaten-LV_Spannung_Teil2'):
    names = glob.glob(location + "/*.csv")

    for name in names:
        df = pd.read_csv(name, header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
        times = df.loc["TimeStamp"]
        times.to_datetime

def check_data(location=r'Messdaten'):
    print("Checking location: " + location)
    names = glob.glob(location + "/*.csv")
    table_difference = []
    table_time_avg = []
    table_time_max = []
    last_table_end = -1
    print(len(names))
   # df = pd.concat([pd.read_csv(f,header=4,sep = ";",usecols = [0,1,2,3,4,5]) for f in glob.glob(location+"/*.csv")], ignore_index = True)
    for name in names:
        print(names.index(name),end = " ")

        df = pd.read_csv(name, header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
        df_p1 = df[df['Description'] == "Electric voltage momentary phase 1 (notverified)"].reset_index()
        df_p2 = df[df['Description'] == "Electric voltage momentary phase 2 (notverified)"].reset_index()
        df_p3 = df[df['Description'] == "Electric voltage momentary phase 3 (notverified)"].reset_index()
        if df_p1.size != df_p2.size or df_p2.size != df_p3.size:
            print()
            print("{} has unequeal phases: {} {} {}".format(name,df_p1.size,df_p2.size,df_p3.size))
        times1 = pd.to_datetime(df_p1.loc[:, "TimeStamp"])
        times2 = pd.to_datetime(df_p2.loc[:, "TimeStamp"])
        times3 = pd.to_datetime(df_p3.loc[:, "TimeStamp"])
        if not times1.equals(times2):
            print()
            print("{} has unequeal timestamps".format(name))
        if not times2.equals(times3):
            print()
            print("{} has unequeal timestamps".format(name))

        if last_table_end != -1:
            table_difference.append(times1[1]-last_table_end)
        differences = []
        for t in range(1,times1.size):
            differences.append((times1[t]-times1[t-1]).total_seconds())
        differences = list(filter(lambda x: x > 0, differences))
        table_time_avg.append(np.mean(differences))
        table_time_max.append(np.max(differences))
        last_table_end = times1[times1.size-1]

    print(table_time_avg)
    print(table_time_max)
    print(table_difference)

def unique_series(location=r'Messdaten'):
    names = glob.glob(location + "/*.csv")
    services = set()
    services_table = []
    aliases_table = []
    aliases = set()
    for name in names:
        print(names.index(name),end = " ")
        df = pd.read_csv(name, header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
        alias = df.loc[:, "AliasName"]
        aliases_table.append(len(alias.unique()))
        aliases.update(alias.unique())
        service = df.loc[:, "ServiceDeliveryPoint"]
        services_table.append(len(service.unique()))
        services.update(service.unique())
    print(aliases_table)
    print(aliases)
    print(services_table)
    print(services)

def unique_series_by_day(location=r'Messdaten'):
    names = glob.glob(location + "/*.csv")
    services = set()
    services_table = []
    aliases_table = []
    aliases = set()
    for name in names:
        print(names.index(name), end=" ")
        df = pd.read_csv(name, header=4, sep=";", usecols=[0, 1, 2, 3, 4, 5])
        alias = df.loc[:, "AliasName"]
        aliases_table.append(len(alias.unique()))
        aliases.update(alias.unique())
        service = df.loc[:, "ServiceDeliveryPoint"]
        services_table.append(len(service.unique()))
        services.update(service.unique())
    print(aliases_table)
    print(aliases)
    print(services_table)
    print(services)

def main():
    print("Starting")
    check_data()
    # check_data("ggf-defekte-Dateien")
    #unique_series()
    #unequal_files = is_part_of_df(r'Messdaten-LV_Spannung_Teil1',r'FiN-Messdaten-LV_Spannung_Teil2')
    #print("Found {} files with differences".format(len(unequal_files)))


main()
