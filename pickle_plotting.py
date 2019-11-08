import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import os
import time
import numpy as np
from pathlib import Path
import logarithmoforecast


l_width = 0.9


def plot_trafostufung(df_p_day, p_counter):
    stufungen = list(np.where(abs(df_p_day.row_dif) > 1)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=stufungen, marker='o', markerfacecolor='black',
                        label="phase" + str(p_counter))
    return len(stufungen) > 0


def plot_without_highlight(df_p_day, p_counter):
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, label="phase" + str(p_counter))
    return True


def plot_spannungsband(df_p_day, p_counter):
    transgressions = list(np.where(df_p_day.Value < 230)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 1


def plot_phase_dif(df_p_day, p_counter):
    transgressions = list(np.where(df_p_day.phase_dif > 1.5)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 1


def plot_seasonal_dif(df_p_day, p_counter):
    transgressions = list(np.where(abs(df_p_day.SeasDif) > 3)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 1

def plot_station_dif(df_p_day, p_counter):
    transgressions = list(np.where(abs(df_p_day.StationDif) > 6)[0])
    df_p_day.Value.plot(figsize=(24, 6), linewidth=l_width, markevery=transgressions, marker='o',
                        markerfacecolor='black', label="phase" + str(p_counter))
    return len(transgressions) > 1


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
            # print(list(np.array(np.where(abs(df_p_day.row_dif) > 1)[0])))
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


def plot_pickle2(pickle_directory, plot_directory):
    fd = os.listdir('.')
    print(fd)
    file_paths = os.listdir(pickle_directory)
    print(file_paths)
    for path in file_paths:
        print(path)
        path = pickle_directory / Path(path)
        df_1 = pd.read_pickle(path / "phase1")
        # print(df_1)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase"+p)), ['1', '2', '3']))
        # phase_values = pd.DataFrame()
        # print('s1')
        # for i, df_p in enumerate(df_phases):
        #     phase = 'p' + str(i+1)
        #     phase_values[phase] = df_p.Value
        #     df_p['row_dif'] = df_p.Value.diff()
        # print(phase_values)
        # phase_values['max_dif'] = phase_values.apply(lambda row: max(abs(row['p1']-row['p2']), abs(row['p1']-row['p3']),
        #                                                              abs(row['p2']-row['p3'])), axis=1)
        # for df_p in df_phases:
        #     df_p['phase_dif'] = phase_values['max_dif']
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