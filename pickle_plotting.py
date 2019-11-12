import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import os
import time
import numpy as np
from pathlib import Path
import calmap


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


def plot_day(plot_directory, df_phases_day, sdp_name, start_time):
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
            relevant_plot = plot_trafostufung(df_p_day, p_counter)
        p_counter = p_counter +1
    legend = plt.legend(fontsize='x-large', loc='lower left')

    for line in legend.get_lines():
        line.set_linewidth(4.0)

    plot_path = plot_directory / sdp_name / start_time

    if relevant_plot:
        plt.savefig(plot_path)
    plt.close(1)


def plot_heatmap(base_plot_directory, df_phases, sdp_name):

    df_phases_add = None
    max_a = 0
    df_heat_map = []
    for p, df_p in enumerate(df_phases):
        df_p['spanMaxBool'] = (df_p.Value > 240).astype(int)
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
    plot_path = base_plot_directory / ('heatmap_'+sdp_name)

    plt.savefig(plot_path)

    print(df_phases_add)


def plot_pickle2(pickle_directory, plot_directory):
    fd = os.listdir('.')
    print(fd)
    file_paths = os.listdir(pickle_directory)
    print(file_paths)
    for path in file_paths:
        print(path)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase"+p)), ['1', '2', '3']))
        plot_heatmap(Path('plots'),df_phases,path.name)
        print(df_phases[0])
        day = pd.Timedelta('1d')
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        print(min_date)
        print(max_date)
        for start_time in pd.date_range(min_date, max_date, freq='d'):
            end_time = start_time + day
            # df_day = df.loc[df.index>start_time and df.index<end_time, :]
            df_phases_day = list(map(lambda df: df.loc[start_time:end_time], df_phases))
            # print(start_time.date())
            plot_day(plot_directory, df_phases_day, path.name, str(start_time.date()))


def main():
    pickle_directory = Path("testPickles")
    plot_directory = Path("plots") / "Trafostufung1"
    print(pickle_directory)
    plot_pickle2(pickle_directory, plot_directory)

main()