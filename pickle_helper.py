import pandas as pd
from pathlib import Path
import os
import numpy as np
import datetime
from pickle_plotting import get_file_paths
import logarithmoforecast as lf


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
    file_paths = get_file_paths(pickle_dir)
    print(file_paths)
    for path in file_paths:
        print(path)
        path = pickle_dir / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p)), ['1', '2', '3']))
        print("Opened pickle")
        phase_values = pd.DataFrame()
        for i, df_p in enumerate(df_phases):
            df_p.drop(columns=['Unit', 'AliasName'], inplace=True)
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
            print(df_p)
            df_p.to_pickle(path / ("h_phase"+str(i+1)))


def add_seasonal_data(pickle_dir=Path('pickles')):
    seasonal_data = pd.DataFrame()
    file_paths = get_file_paths(pickle_dir)
    print(file_paths)
    day = pd.Timedelta('1d')
    for path in file_paths:
        print(path)
        path = pickle_dir / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p))[['Value']], ['1', '2', '3']))
        weekday_dfs_phases = [[None for x in range(7)] for y in range(3)]
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        for p, df_p in enumerate(df_phases):
            for start_time in pd.date_range(min_date, max_date, freq='d'):
                end_time = start_time + day
                df_p_day = df_p.loc[start_time:end_time]
                df_p_day_med = df_p_day.resample('30s').median().rename(columns={'Value': str(start_time.date())})
                df_p_day_med.index = df_p_day_med.index.time
                weekday = start_time.date().weekday()
                # print(weekday_dfs_phases[p][weekday])
                if weekday_dfs_phases[p][weekday] is None:
                    weekday_df = df_p_day_med
                    weekday_dfs_phases[p][weekday] = weekday_df
                else:
                    weekday_df = weekday_dfs_phases[p][weekday]
                    weekday_df = weekday_df.join(df_p_day_med, how='outer')
                    weekday_dfs_phases[p][weekday] = weekday_df
        print("Split DF")
        for p, df_weekdays in enumerate(weekday_dfs_phases):
            for w, df in enumerate(df_weekdays):
                df['med'] = df.median(axis=1)
                #  print(df)
        df_phases_h = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        print(df_phases_h)
        for p, df_p in enumerate(df_phases_h):
            print(p)
            df_weekdays = weekday_dfs_phases[p]
            df_p['SeasDif'] = df_p.apply(lambda row: (row['Value'] - df_weekdays[row.name.weekday()].loc[
                (row.name - datetime.timedelta(seconds=row.name.second % 30,
                                               microseconds=row.name.microsecond)).time()]['med']), axis=1)
            #df_p['SeasDif'] = df_p.apply(lambda row: abs(row['Value']- df_weekdays[row.name.weekday()].loc[row.name.time()]), axis=1)
            print(df_p)
            df_p.to_pickle(path / ("h_phase" + str(p + 1)))


def add_cross_station_data(pickle_dir=Path('pickles')):
    station_avgs = pd.read_pickle(pickle_directory / "meanStationValues")
    file_paths = get_file_paths(pickle_dir)
    for path in file_paths:
        print(path)
        path = pickle_dir / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        for p, df_p in enumerate(df_phases):
            print(p)
            print(df_p)
            v1s = []
            for index, row in df_p.iterrows():
                v1 = row['Value'] - station_avgs.loc[index - datetime.timedelta(seconds=index.second % 30,
                                                     microseconds=index.microsecond)]
                v1s.append(v1)
            df_p['StationDif'] = v1s
            # df_p.apply(lambda row:print(row), axis=1)
            # df_p['StationDif'] = df_p.apply(lambda row: (row['Value'] - station_avgs.loc[
            #     (row.name - datetime.timedelta(seconds=row.name.second % 30,
            #                                         microseconds=row.name.microsecond)).time()]), axis=1)
            print(df_p)
            df_p.to_pickle(path / ("h_phase" + str(p + 1)))


def create_mean_pickle(pickle_dir=Path('pickles')):
    station_avgs = pd.DataFrame()
    file_paths = get_file_paths(pickle_dir)
    print(file_paths)
    day = pd.Timedelta('1d')
    for path in file_paths:
        station_name = path
        print(path)
        path = pickle_dir / Path(path)
        df_phases = pd.DataFrame()
        for p, df_p in enumerate(list(map(lambda p: pd.read_pickle(path / ("phase" + p))[['Value']], ['1', '2', '3']))):
            df_phases = df_phases.join(other=df_p.rename(columns={'Value': 'ValueP'+str(p+1)}), how='outer')
        df_phases = df_phases.resample('30s').mean()
        df_phases[station_name] = df_phases.mean(axis=1)
        # print(df_phases[[station_name]])
        # print(station_avgs)
        station_avgs = station_avgs.join(df_phases[[station_name]], how='outer')
    station_avgs = station_avgs.mean(axis=1)
    print(station_avgs)
    station_avgs.to_pickle(pickle_dir / 'meanStationValues123')


def create_mean_season_pickle(pickle_dir=Path('pickles')):
    station_avgs = pd.DataFrame()
    file_paths = get_file_paths(pickle_dir)
    print(file_paths)
    day = pd.Timedelta('1d')
    for path in file_paths:
        station_name = path
        print(path)
        path = pickle_dir / Path(path)
        df_phases = pd.DataFrame()
        for p, df_p in enumerate(list(map(lambda p: pd.read_pickle(path / ("phase" + p))[['Value']], ['1', '2', '3']))):
            df_phases = df_phases.join(other=df_p.rename(columns={'Value': 'ValueP'+str(p+1)}), how='outer')
        df_phases = lf.generators.add_daytypes(df_phases)
        df_phases = lf.generators.add_holidays(df_phases,'BW')
        print('typed_phases_accumulation')
        df_phases_restday = df_phases[
            ((df_phases.is_saturday == 1) | (df_phases.is_sunday == 1) | (df_phases.is_holiday == True))]
        df_phases_workday = df_phases[
            True ^ ((df_phases.is_saturday == 1) | (df_phases.is_sunday == 1) | (df_phases.is_holiday == True))]
        print('Split_phases')
        for df_phases_typeday in [df_phases_restday,df_phases_workday]:
            df_phases_typeday = df_phases_typeday[['ValueP1','ValueP2','ValueP3']]
            df_phases_typeday = df_phases_typeday.resample('30s').mean()
            df_phases_typeday[station_name+"_pre_window"] = df_phases_typeday.mean(axis=1)
            df_phases_typeday = df_phases_typeday.drop(['ValueP1','ValueP2','ValueP3'],axis=1)
            df_phases_typeday = df_phases_typeday.dropna()
            v1s = []
            min_date = df_phases_typeday.index.min()
            max_date = df_phases_typeday.index.max()
            three_w_timedelta = pd.Timedelta('3w')
            old_window_min_date = min_date.date()
            for index, row in df_phases_typeday.iterrows():
                window_min_date = max(min_date, index- three_w_timedelta)
                window_max_date = min(max_date, index+ three_w_timedelta)
                if old_window_min_date != window_min_date.date():
                    print(str(window_min_date)+' -> '+str(window_max_date))
                    old_window_min_date = window_min_date.date()
                window_slice = df_phases_typeday.loc[window_min_date:window_max_date]
                v1 = window_slice.mean()
                v1s.append(v1)
            df_phases_typeday[station_name] = v1s
        df_phases = df_phases_typeday[[station_name]].join(df_phases_workday[[station_name]], how='outer')
        station_avgs = station_avgs.join(df_phases, how='outer')
    station_avgs = station_avgs.mean(axis=1)
    print(station_avgs)
    station_avgs.to_pickle(pickle_dir / 'meanStationSeasonValues')


def create_mean_season_pickle2(pickle_dir=Path('pickles')):
    df_mean_season = pd.Series()
    df_mean_pickle = pd.read_pickle(pickle_dir / 'meanStationValues').to_frame(name='mean_values')
    print(df_mean_pickle['mean_values'].size)
    print(len(df_mean_pickle))
    df_mean_pickle = df_mean_pickle.iloc[:100800]
    print(df_mean_pickle)
    column_name = 'windowed_means'
    df_mean_pickle = lf.generators.add_daytypes(df_mean_pickle)
    df_mean_pickle = lf.generators.add_holidays(df_mean_pickle, 'BW')
    df_mean_pickle_restday = df_mean_pickle[
        ((df_mean_pickle.is_saturday == 1) | (df_mean_pickle.is_sunday == 1) | (df_mean_pickle.is_holiday == True))]
    df_mean_pickle_workday = df_mean_pickle[
        True ^ ((df_mean_pickle.is_saturday == 1) | (df_mean_pickle.is_sunday == 1) | (df_mean_pickle.is_holiday == True))]
    print('Split_dataframe')
    for i, df_mean_pickle_typeday in enumerate([df_mean_pickle_restday, df_mean_pickle_workday]):
        df_mean_pickle_typeday = df_mean_pickle_typeday[['mean_values']].dropna()
        v1s = []
        min_date = df_mean_pickle_typeday.index.min()
        max_date = df_mean_pickle_typeday.index.max()
        three_w_timedelta = pd.Timedelta('3w')
        old_window_min_date = min_date.date()
        print(min_date)
        for index, row in df_mean_pickle_typeday.iterrows():
            window_min_date = max(min_date, index - three_w_timedelta)
            window_max_date = min(max_date, index + three_w_timedelta)
            if old_window_min_date != window_min_date.date():
                print(str(window_min_date) + ' -> ' + str(window_max_date))
                old_window_min_date = window_min_date.date()
            window_slice = df_mean_pickle_typeday.loc[window_min_date:window_max_date]
            v1 = window_slice['mean_values'].mean()
            v1s.append(v1)
        df_mean_pickle_typeday[column_name] = v1s
        print(df_mean_pickle_typeday[[column_name]])
        print(df_mean_season)
        df_mean_season = pd.concat([df_mean_season,df_mean_pickle_typeday[column_name]],sort=True)
        # if i ==0:
        #     df_mean_pickle_restday = df_mean_pickle_typeday
        # else:
        #     df_mean_pickle_workday = df_mean_pickle_typeday
    print(df_mean_season.size)
    print(df_mean_season)
    df_mean_season.to_pickle(pickle_dir / 'meanStationSeasonValues')


def drop_useless_labels(pickle_dir=Path('pickles')):
    file_paths = get_file_paths(pickle_dir)
    print(file_paths)
    day = pd.Timedelta('1d')
    for path in file_paths:
        path = pickle_dir / Path(path)
        df_phases_h = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        for p, df_p in enumerate(df_phases_h):
            df_p.drop(columns=['Unit', 'AliasName'], inplace=True)
            df_p.to_pickle(path / ("h_phase" + str(p + 1)))

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(df_weekdays.isna().sum())
def main():
    print('pickle_helper')
    datasets_dir = Path('FiN-Messdaten-LV_Spannung_Teil2')
    pickle_dir = Path('testPickles')
    # drop_useless_labels('testPickles')
    # pickle_directory(datasets_dir, pickle_dir)
    create_mean_season_pickle2(pickle_dir)
    #  add_help_data(pickle_dir)

if __name__ == "__main__":
    main()
