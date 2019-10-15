import pandas as pd
from pathlib import Path
import os
import numpy as np


def calculate_voltage_steps(df_phases):
    result_df = pd.DataFrame()
    phase_counter = 1
    for df_p in df_phases:
        steps_up = list(np.where(df_p.Value.diff() > 1)[0])
        steps_down = list(np.where(df_p.Value.diff() < -1)[0])
        column_name = "1VStepsP"+str(phase_counter)
        # column_name_down = "StepDownP" + str(phase_counter)
        up_column = {column_name: 'Up'}
        down_column = {column_name: 'Down'}
        steps_up_df = df_p.iloc[steps_up, :].assign(**up_column)[[column_name]]
        steps_down_df = df_p.iloc[steps_down, :].assign(**down_column)[[column_name]]
        steps_df = pd.concat([steps_up_df, steps_down_df]).sort_index()
        result_df = pd.concat([steps_df, result_df], axis= 1).sort_index()
        phase_counter = phase_counter + 1
    return result_df


def calculate_voltage_range(df_phases, df_sdp):
    phase_counter = 1
    for df_p in df_phases:
        transgressions = list(np.where(df_p.Value > 240)[0])
        column_name = "Over240P" + str(phase_counter)
        over_column = {column_name: 'Over'}
        transgressions_df = df_p.iloc[transgressions, :].assign(**over_column)[[column_name]]
        df_sdp = pd.concat([transgressions_df, df_sdp], axis=1).sort_index()
        phase_counter = phase_counter + 1

    return df_sdp


def calculate_phase_distance(df_phases, df_sdp):
    phase_counter = 1
    for df_p in df_phases:
        transgressions = list(np.where(df_p.Value > 240)[0])
        column_name = "Over240P" + str(phase_counter)
        over_column = {column_name: 'Over'}
        transgressions_df = df_p.iloc[transgressions, :].assign(**over_column)[[column_name]]
        df_sdp = pd.concat([transgressions_df, df_sdp], axis=1).sort_index()
        phase_counter = phase_counter + 1

    return df_sdp


def calculate_anomalies(pickle_directory, excel_file_path):
    print(os.getcwd())
    file_paths = os.listdir(pickle_directory)
    print(file_paths)

    for path in file_paths:
        print(path)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p)), ['1', '2', '3']))
        df_sdp = calculate_voltage_steps(df_phases)
        df_sdp = calculate_voltage_range(df_phases,df_sdp)
        excel_writer = pd.ExcelWriter(path=excel_file_path, datetime_format='YYYY-MM-DD HH:MM:SS')
        df_sdp.to_excel(sheet_name=path.name, excel_writer=excel_writer)
        # workbook = excel_writer.book
        excel_writer.save()


def main():
    pickle_directory = Path("testPickles")
    excel_file_path = Path("test.xlsx")
    calculate_anomalies(pickle_directory, excel_file_path)


main()