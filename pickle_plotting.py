import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import os
import time
import numpy as np
from pathlib import Path


l_width = 0.9


def plot_trafostufung(df_p_day, p_counter):
    stufungen = list(np.where(abs(df_p_day.row_dif) > 1)[0])
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
    transgressions = list(np.where(abs(df_p_day.SeasDif) > 3)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 0

def plot_station_dif(df_p_day, p_counter):
    transgressions = list(np.where(abs(df_p_day.StationDif) > 6)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 0


def plot_day(plot_directory, df_phases_day, sdp_name, start_time, df_mean_values, plot_method):
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
        df_p['spanMaxBool'] = (anomalie_criteria(df_p)).astype(int)
        df_month_anomalies = df_p['Value'].resample('MS').sum().rename(columns={'Value': sdp_name})
        df_p = df_p.resample('1d').sum()
        max_a = max(max_a, max(df_p['spanMaxBool']))
        columns = df_p.index[:].month
        index = df_p.index.day
        df_p = df_p.pivot_table(index=index, columns=columns,values='spanMaxBool')
        if df_phases_add is None:
            df_phases_add = df_p
        else:
            df_phases_add = df_phases_add.add(df_p, fill_value=0)
        df_heat_map.append(df_p)
        # plt.pcolormesh(data=t2d)
        # plt.show()

    plt.figure(1)
    fig, axs = plt.subplots(1,3, figsize=(8,8))
    for p, df_p in enumerate(df_heat_map):
        print(df_p)
        ax = axs[p]
        ax.set_aspect('equal')
        ax.set_xticks(np.arange(len(df_p.columns)))
        ax.set_yticks(np.arange(len(df_p.index)))
        ax.set_xticklabels(df_p.columns)
        ax.set_yticklabels(df_p.index)
        heatmap = ax.pcolormesh(df_p, cmap=plt.cm.Reds, alpha=1, vmin=0, vmax= max_a)
        # plt.colorbar(heatmap)

    fig.colorbar(heatmap, ax=axs.ravel().tolist())
    plt.close(1)
    plot_path = base_plot_directory / sdp_name / ('heatmap_Anomalies')
    if not os.path.exists(base_plot_directory / sdp_name):
        os.makedirs(base_plot_directory / sdp_name)
    plt.savefig(plot_path)
    plt.close(fig)



def plot_pickle2(pickle_directory, plot_directory, plot_method, anomalie_criteria):
    fd = os.listdir('.')
    print(plot_directory)
    print(fd)
    file_paths = os.listdir(pickle_directory)
    print(file_paths)
    df_mean_values = pd.read_pickle(Path('pickles') / 'medianStationValues')
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df_mean_values)
    max_a = 0
    for path in file_paths:
        print(path)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase"+p)), ['1', '2', '3']))
        df_station_anomalies = plot_heatmap(plot_directory, df_phases, path.name, anomalie_criteria)
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

def main():
    pickle_directory = Path("pickles")

    plot_directory = Path("plots") / "Min230"
    plot_pickle2(pickle_directory, plot_directory, plot_spannungsband_min, lambda df_p_day: df_p_day.Value < 230)
    plot_directory = Path("plots") / "Max240"
    plot_pickle2(pickle_directory, plot_directory, plot_spannungsband_max, lambda df_p_day: df_p_day.Value > 240)
    plot_directory = Path("plots") / "PhaseDif1_5"
    plot_pickle2(pickle_directory, plot_directory, plot_phase_dif, lambda df_p_day: df_p_day.phase_dif > 1.5)
    plot_directory = Path("plots") / "SeasDif3"
    plot_pickle2(pickle_directory, plot_directory, plot_seasonal_dif, lambda df_p_day: abs(df_p_day.SeasDif) > 3)
    plot_directory = Path("plots") / "StationDif6"
    plot_pickle2(pickle_directory, plot_directory, plot_station_dif, lambda df_p_day: abs(df_p_day.StationDif) > 6)
    plot_directory = Path("plots") / "Trafostufung1"
    plot_pickle2(pickle_directory, plot_directory, plot_trafostufung, lambda df_p_day: abs(df_p_day.row_dif) > 1)

main()