import pandas as pd
from pathlib import Path
import os
import numpy as np
import datetime


def pickle_directory(datasets_dir, pickle_dir):
    file_paths = os.listdir(datasets_dir)
    sdp_series = {}
    for path in file_paths:
        number = Path(path).stem
        print(number)
        df = pd.read_csv(datasets_dir / path, header=4, sep=';', usecols=[0, 1, 2, 3, 4, 5], decimal=",")
        # df = pd.read_csv(r"/home/joelhaubold/Dokumente/BADaten/FiN-Messdaten-LV_Spannung_Teil2/tmpFile-1492693540182.csv", header=4, sep=';', usecols=[0, 1, 2, 3, 4, 5], decimal=",")
        df.drop(columns=['AliasName', 'Unit'])
        df = df.set_index('TimeStamp')
        df = df.sort_index()
        sdp_list = df.ServiceDeliveryPoint.unique()
        print(sdp_list)
        for sdp in sdp_list:
            df_sdp = df.loc[df.ServiceDeliveryPoint == sdp, :]  # Slim the pd down here for less memory consumption?
            if sdp in sdp_series:
                combined_df = sdp_series.get(sdp)
                combined_df = pd.concat([combined_df, df_sdp]).sort_index()
                sdp_series[sdp] = combined_df
            else:
                sdp_series[sdp] = df_sdp
    for key, value in sdp_series.items():
        print(key)
        if not os.path.exists(pickle_dir / key):
            os.makedirs(pickle_dir / key)
        value.index = pd.to_datetime(value.index)
        pos1 = value.Description == 'Electric voltage momentary phase 1 (notverified)'
        df_phase1 = value.loc[pos1, :]
        pos2 = value.Description == 'Electric voltage momentary phase 2 (notverified)'
        df_phase2 = value.loc[pos2, :]
        pos3 = value.Description == 'Electric voltage momentary phase 3 (notverified)'
        df_phase3 = value.loc[pos3, :]

        # for phase in ['1', '2', '3']:
            # if not os.path.exists('pickles/' + key + '/phase'+phase):
                # os.makedirs('pickles/' + key + '/phase'+phase)

        df_phase1.to_pickle(pickle_dir / key / "phase1")
        df_phase2.to_pickle(pickle_dir / key / "phase2")
        df_phase3.to_pickle(pickle_dir / key / "phase3")
        # value.to_pickle(r"pickles/"+key+"/3PhasesDF")


def add_help_data(pickle_dir=Path('pickles')):
    file_paths = os.listdir(pickle_dir)
    print(file_paths)
    for path in file_paths:
        print(path)
        path = pickle_dir / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p)), ['1', '2', '3']))
        print("Opened pickle")
        phase_values = pd.DataFrame()
        for i, df_p in enumerate(df_phases):
            phase = 'p' + str(i+1)
            phase_values[phase] = df_p.Value
        for df_p in df_phases:
            df_p['row_dif'] = df_p.Value.diff()
        print("Created help values")
        np.diff(phase_values.values)
        phase_values['max_dif'] = phase_values.apply(
            lambda row: max(abs(row['p1'] - row['p2']), abs(row['p1'] - row['p3']),
                            abs(row['p2'] - row['p3'])), axis=1)
        print("Calculated help data")
        for df_p in df_phases:
            df_p['phase_dif'] = phase_values['max_dif']
        print("Assigned help data")
        for i, df_p in enumerate(df_phases):
            df_p.to_pickle(path / ("h_phase"+str(i)))


def add_seasonal_data(pickle_dir=Path('pickles')):
    seasonal_data = pd.DataFrame()
    file_paths = os.listdir(pickle_dir)
    print(file_paths)
    day = pd.Timedelta('1d')
    for path in file_paths:
        print(path)
        path = pickle_dir / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p)), ['1', '2', '3']))
        weekday_dfs_phases = list(map(lambda p: list(map(lambda w: [], range(7))), range(3)))
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        for p, df_p in enumerate(df_phases):
            phase = 'p' + str(p+1)
            for start_time in pd.date_range(min_date, max_date, freq='d'):
                phase_day = phase + '_' + str(start_time.date())
                end_time = start_time + day
                df_p_day = df_p.loc[start_time:end_time]
                weekday = start_time.weekday()
                weekday_df = weekday_dfs_phases[p][weekday]
                df_p_day = df_p_day.set_index(df_p_day.index.time)
                weekday_df.append(df_p_day)
        print("Split DF")
        for p, df_p in enumerate(df_phases):
            weekday_dfs = weekday_dfs_phases[p]
            for w, weekday_df_list in enumerate(weekday_dfs):  # Check for time distance
                series_name = 'p' + str(p) + 'w' + str(w)
                len_list = list(map(lambda df: len(df), weekday_df_list))
                med_i = np.argsort(len_list)[len(len_list)//2]
                orient_df = weekday_df_list[med_i]
                for index, row in orient_df.iterrows():
                    print(weekday_df_list[0])
                    print(weekday_df_list[0].index.get_loc(index, method='nearest'))
                    print(list(map(lambda df: df.index.get_loc(index, method='nearest'), weekday_df_list)))
                    # np.average(list(map(lambda df: df.at_time(index),weekday_df_list)))
                # seasonal_data[series_name] =

                # print(list(map(lambda df : len(df), weekday_df_list)))




def main():
    datasets_dir = Path('FiN-Messdaten-LV_Spannung_Teil2')
    pickle_dir = Path('pickles')
    # pickle_directory(datasets_dir, pickle_dir)
    add_seasonal_data('testPickles')
    # add_help_data(pickle_dir)
    # pickle_directory(r'/home/joelhaubold/Dokumente/BADaten/FiN-Messdaten-LV_Spannung_Teil2')
    # pickle_directory(r'C:\Users\joelh\PycharmProjects\Netzzustandsmessung\FiN-Messdaten-LV_Spannung_Teil2')


main()
