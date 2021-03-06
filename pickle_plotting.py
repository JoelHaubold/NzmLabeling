import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

l_width = 0.9


def get_file_paths(file_directory):
    file_paths = os.listdir(file_directory)
    file_paths = list(filter(lambda f_path: os.path.isdir(file_directory / f_path), file_paths))
    return file_paths


def plot_trafostufung(df_p_day, p_counter):
    stufungen = list(np.where(abs(df_p_day.row_dif) > 1)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=stufungen, marker='o', markerfacecolor='black',
                        label="phase" + str(p_counter))
    return len(stufungen) > 0


def plot_with_lambda(df_p_day, p_counter, anomaly_criteria):
    stufungen = list(np.where(anomaly_criteria(df_p_day))[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=stufungen, marker='o', markerfacecolor='black',
                        label="phase" + str(p_counter))
    return len(stufungen) > 0


def plot_without_highlight(df_p_day, p_counter):
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, label="phase" + str(p_counter))
    return True


def plot_spannungsband_min(df_p_day, p_counter):
    transgressions = list(np.where(df_p_day.Value < 230)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 0


def plot_spannungsband_max(df_p_day, p_counter):
    transgressions = list(np.where(df_p_day.Value > 240)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 0


def plot_phase_dif(df_p_day, p_counter):
    transgressions = list(np.where(df_p_day.phase_dif > 1.5)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 0


def plot_seasonal_dif(df_p_day, p_counter):
    transgressions = list(np.where(abs(df_p_day.SeasDif) > 3.5)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 0


def plot_station_dif(df_p_day, p_counter):
    transgressions = list(np.where(abs(df_p_day.StationDif) > 6)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 0


def plot_day(plot_directory, df_phases_day, sdp_name, start_time, df_mean_values, plot_method):
    print(start_time)
    sdp_directory = plot_directory / sdp_name
    if not os.path.exists(sdp_directory):
        os.makedirs(sdp_directory)
    plt.figure(1)
    plt.ylabel('Phases')
    p_counter = 1
    relevant_plot = False

    for df_p_day in df_phases_day:  # Check if plottable
        # print(df_p_day.row_dif.where(lambda x: x > 1))
        if not df_p_day.empty:
            # relevant_plot = plot_spannungsband(df_p_day, p_counter)
            # relevant_plot = plot_trafostufung(df_p_day, p_counter)
            relevant_plot = plot_method(df_p_day, p_counter)
        p_counter = p_counter + 1
    if relevant_plot:
        df_mean_values.plot(figsize=(24, 6), linewidth=0.5, color='grey', label="meanStationAverage")
    legend = plt.legend(fontsize='x-large', loc='lower left')

    for line in legend.get_lines():
        line.set_linewidth(4.0)

    plot_path = plot_directory / sdp_name / start_time

    if relevant_plot:
        plt.savefig(plot_path)
    plt.close(1)


def plot_heatmap(base_plot_directory, df_phases, sdp_name, anomalie_criteria):
    df_phases_add = None
    max_a = 0
    df_heat_map = []
    for p, df_p in enumerate(df_phases):
        # df_p['spanMaxBool'] = (df_p.Value > 240).astype(int)
        df_p[sdp_name] = (np.where(anomalie_criteria(df_p), 1, 0)).astype(int)
        df_month_anomalies = df_p['Value'].resample('MS').sum().rename(columns={'Value': sdp_name})
        df_p = df_p.resample('1d').sum()
        max_a = max(max_a, max(df_p[sdp_name]))
        columns = df_p.index[:].month
        index = df_p.index.day
        df_p = df_p.pivot_table(index=index, columns=columns, values=sdp_name)
        if df_phases_add is None:
            df_phases_add = df_p
        else:
            df_phases_add = df_phases_add.add(df_p, fill_value=0)
        df_heat_map.append(df_p)
        # plt.pcolormesh(data=t2d)
        # plt.show()

    plt.figure(1)
    fig, axs = plt.subplots(1, 3, figsize=(8, 8))
    for p, df_p in enumerate(df_heat_map):
        # print(df_p)
        ax = axs[p]
        ax.set_aspect('equal')
        ax.set_xticks(np.arange(len(df_p.columns)))
        ax.set_yticks(np.arange(len(df_p.index)))
        ax.set_xticklabels(df_p.columns)
        ax.set_yticklabels(df_p.index)
        heatmap = ax.pcolormesh(df_p, cmap=plt.cm.Reds, alpha=1, vmin=0, vmax=max_a)
        # plt.colorbar(heatmap)

    fig.colorbar(heatmap, ax=axs.ravel().tolist())
    plt.close(1)
    plot_path = base_plot_directory / sdp_name / ('heatmap_Anomalies')
    if not os.path.exists(base_plot_directory / sdp_name):
        os.makedirs(base_plot_directory / sdp_name)
    plt.savefig(plot_path)
    plt.close(fig)
    # print(df_phases_add)
    return df_phases_add, max_a


plot_method_to_stations = {}


def plot_pickle2(pickle_directory, plot_directory, plot_method, anomalie_criteria):
    fd = os.listdir('.')
    print(plot_directory)
    print(fd)
    file_paths = os.listdir(pickle_directory)
    print(file_paths)
    df_mean_values = pd.read_pickle(Path('medianStationValues'))
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df_mean_values)
    max_a = 0
    number_stations = len(file_paths)
    station_anomalies_list = []
    for path in file_paths:
        print(path)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        df_station_anomalies, max_station_a = plot_heatmap(plot_directory, df_phases, path.name, anomalie_criteria)
        max_a = max(max_a, max_station_a)
        station_anomalies_list.append(df_station_anomalies)
        day = pd.Timedelta('1d')
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        print(min_date)
        print(max_date)
        for start_time in pd.date_range(min_date, max_date, freq='d'):
            end_time = start_time + day
            # df_day = df.loc[df.index>start_time and df.index<end_time, :]
            df_phases_day = list(map(lambda df: df.loc[start_time:end_time], df_phases))
            df_mean_values_day = df_mean_values.loc[start_time:end_time]

            # print(start_time.date())
            # plot_day(plot_directory, df_phases_day, path.name, str(start_time.date()), df_mean_values_day, plot_method)
    fig, axs = plt.subplots(1, number_stations, figsize=(7 * number_stations, 12))
    for n, df_station_anomalies in enumerate(station_anomalies_list):
        ax = axs[n]
        ax.set_aspect('equal')
        ax.set_xticks(np.arange(len(df_station_anomalies.columns)))
        ax.set_yticks(np.arange(len(df_station_anomalies.index)))
        ax.set_xticklabels(df_station_anomalies.columns)
        ax.set_yticklabels(df_station_anomalies.index)
        ax.title.set_text(file_paths[n])
        heatmap = ax.pcolormesh(df_station_anomalies, cmap=plt.cm.Reds, alpha=1, vmin=0, vmax=max_a)
    anomalies_per_station = list(map(lambda df: df.sum().sum(), station_anomalies_list))
    df = station_anomalies_list[0]
    plot_method_to_stations[plot_directory.name] = anomalies_per_station
    fig.colorbar(heatmap, ax=axs.ravel().tolist())
    print('saving')
    plt.savefig(plot_directory / 'station_anomalies')
    plt.close(fig)


def plot_pickle_daywise(pickle_directory, plot_directory, plot_method):
    fd = os.listdir('.')
    print(plot_directory)
    print(fd)
    file_paths = get_file_paths(pickle_directory)
    print(file_paths)
    #  df_mean_valuesOld = pd.read_pickle(pickle_directory / 'meanStationValues')
    for path in file_paths:
        print(path)
        df_mean_values = pd.read_pickle(pickle_directory / (path + 'season_aggregation')).sort_index()
        print(df_mean_values)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        day = pd.Timedelta('1d')
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        print(min_date)
        print(max_date)
        print(df_phases[0]['SeasDif'])
        for start_time in pd.date_range(min_date, max_date, freq='d'):
            end_time = start_time + day
            # df_day = df.loc[df.index>start_time and df.index<end_time, :]
            df_phases_day = list(map(lambda df: df.loc[start_time:end_time], df_phases))
            df_mean_values_day = df_mean_values.loc[start_time:end_time]

            # print(start_time.date())
            plot_day(plot_directory, df_phases_day, path.name, str(start_time.date()), df_mean_values_day, plot_method)


def plot_phase_dif_daywise(pickle_directory, plot_directory):
    fd = os.listdir('.')
    print(plot_directory)
    print(fd)
    file_paths = get_file_paths(pickle_directory)
    print(file_paths)
    df_mean_values = pd.read_pickle(pickle_directory / 'meanStationValues')
    df_phase_dif_border = pd.read_csv('PhaseDifAnomalieBorder.csv', header=None, index_col=0, squeeze=True, )
    print(df_phase_dif_border)
    for path in file_paths:
        print(path)
        anomaly_border = df_phase_dif_border.at[path]
        print(anomaly_border)
        plot_method = lambda df_p_day, p_counter: plot_with_lambda(df_p_day, p_counter, lambda
            df_phase_day: df_phase_day.phase_dif > anomaly_border)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        day = pd.Timedelta('1d')
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        print(min_date)
        print(max_date)
        for start_time in pd.date_range(min_date, max_date, freq='d'):
            end_time = start_time + day
            # df_day = df.loc[df.index>start_time and df.index<end_time, :]
            df_phases_day = list(map(lambda df: df.loc[start_time:end_time], df_phases))
            df_mean_values_day = df_mean_values.loc[start_time:end_time]

            # print(start_time.date())
            plot_day(plot_directory, df_phases_day, path.name, str(start_time.date()), df_mean_values_day, plot_method)


def plot_pickle_dir(pickle_directory, base_plot_dir):
    # plot_directory = Path("plots") / "SeasDif3"
    # plot_pickle2(pickle_directory, plot_directory, plot_seasonal_dif, lambda df_p_day: abs(df_p_day.SeasDif) > 3)
    # plot_directory = base_plot_dir / "PhaseDifDynamic"
    # plot_phase_dif_daywise(pickle_directory, plot_directory)
    plot_directory = Path("plots") / "SeasDif3_5"
    plot_pickle_daywise(pickle_directory, plot_directory, plot_seasonal_dif)
    # plot_directory = base_plot_dir / "Trafostufung1"
    # plot_pickle_daywise(pickle_directory, plot_directory, plot_trafostufung)


def plot_series_hist(pickle_dir, base_plot_dir, column_name):
    file_paths = get_file_paths(pickle_dir)
    fig, axs = plt.subplots(1, len(file_paths), figsize=(6 * len(file_paths), 12))
    for i, path in enumerate(file_paths):
        if len(file_paths) == 1:
            ax = axs
        else:
            ax = axs[i]
        path = pickle_dir / path
        df_phase1 = pd.read_pickle(path / ("h_phase" + str(1)))
        phase_dif = df_phase1[column_name]
        phase_dif = phase_dif.where(lambda x: x > 11)
        phase_dif.hist(ax=ax, bins=10)
        ax.set_title(path.name)
    plt.savefig(base_plot_dir / 'histPhasesAll11')


def main():
    pickle_directory = Path("pickles")
    base_plot_dir = Path("plots")

    # plot_series_hist(pickle_directory,base_plot_dir,'phase_dif')

    # plot_pickle_dir(pickle_directory,base_plot_dir)
    n = 0
    file_paths = get_file_paths(pickle_directory)
    for path in file_paths:
        print(path)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        old_n = n
        n = n + df_phases[0].shape[0]
        n = n + df_phases[1].shape[0]
        n = n + df_phases[2].shape[0]
        print(n - old_n)
    print(n)
    # for plot_method, anomalies_in_station in plot_method_to_stations.items():
    #     fig, ax = plt.subplots(1, 1,figsize=(6*len(anomalies_in_station), 12))
    #     ax.set_aspect('equal')
    #     print(anomalies_in_station)
    #     df_anomalies_in_station = pd.DataFrame(data=anomalies_in_station, index=file_paths).transpose()
    #     print(df_anomalies_in_station)
    #     ax.title.set_text(plot_method)
    #     ax.set_xticks(np.arange(len(file_paths)))
    #     ax.set_xticklabels(file_paths, ha='left')#, rotation=45)
    #     heatmap = ax.pcolormesh(df_anomalies_in_station, cmap=plt.cm.Reds, alpha=1, vmin=0)
    #     plt.savefig(Path('plots') / (plot_method+'_anomalie_sum'))
    #     plt.close(fig)


if __name__ == "__main__":
    main()
