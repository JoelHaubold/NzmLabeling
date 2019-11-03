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
        df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p))[['Value']], ['1', '2', '3'])) #  Sort into weekdays
        weekday_dfs_phases = []
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        for p, df_p in enumerate(df_phases):
            for start_time in pd.date_range(min_date, max_date, freq='d'):
                end_time = start_time + day
                df_p_day = df_p.loc[start_time:end_time]
                df_p_day_med = df_p_day.resample('1min').median().rename(columns={'Value': str(start_time.date())})
                df_p_day_med.index = df_p_day_med.index.time
                if len(weekday_dfs_phases) <= p:
                    weekday_df = df_p_day_med
                    weekday_dfs_phases.append(weekday_df)
                else:
                    weekday_df = weekday_dfs_phases[p]
                    weekday_df = weekday_df.join(df_p_day_med, how='outer')
                    weekday_dfs_phases[p] = weekday_df
        print("Split DF")
        for p, df_weekdays in enumerate(weekday_dfs_phases):
            # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            #     print(df_weekdays.isna().sum())
            df_weekdays['med'] = df_weekdays.median()
            print(df_weekdays) #  Save to pickle




def main():
    datasets_dir = Path('FiN-Messdaten-LV_Spannung_Teil2')
    pickle_dir = Path('pickles')
    # pickle_directory(datasets_dir, pickle_dir)
    add_seasonal_data('testPickles')
    # add_help_data(pickle_dir)
    # pickle_directory(r'/home/joelhaubold/Dokumente/BADaten/FiN-Messdaten-LV_Spannung_Teil2')
    # pickle_directory(r'C:\Users\joelh\PycharmProjects\Netzzustandsmessung\FiN-Messdaten-LV_Spannung_Teil2')


main()
