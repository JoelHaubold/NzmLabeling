import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import os
import numpy as np


def get_file_paths(file_directory):
    file_paths = os.listdir(file_directory)
    file_paths = list(filter(lambda f_path: os.path.isdir(file_directory / f_path), file_paths))
    return file_paths


def plot_day(plot_directory, df_phases_day, sdp_name, start_time, df_comparison_values, plot_method, comparison_label):
    sdp_directory = plot_directory / sdp_name
    if not os.path.exists(sdp_directory):
        os.makedirs(sdp_directory)
    plt.figure(1)
    plt.ylabel('Phases')
    p_counter = 1
    relevant_plot = False
    transgressions_sum = 0

    for df_p_day in df_phases_day:
        if not df_p_day.empty:
            transgressions = plot_method(df_p_day, p_counter)
            transgressions_sum += transgressions
            relevant_plot = relevant_plot or transgressions > 0
        p_counter = p_counter + 1
    if relevant_plot and not df_comparison_values.empty:
        df_comparison_values.plot(figsize=(24, 6), linewidth=0.5, color='grey', label=comparison_label)
    if relevant_plot:
        legend = plt.legend(fontsize='x-large', loc='lower left')
        for line in legend.get_lines():
            line.set_linewidth(4.0)

    plot_path = plot_directory / sdp_name / start_time

    if relevant_plot:
        plt.savefig(plot_path)
    plt.close(1)
    if transgressions_sum > 0:
        print(start_time)
        print(transgressions_sum)
    return transgressions_sum


def plot_pickle_daywise(pickle_directory, plot_directory, plot_method, comparison_series_func):
    transgression_sum = 0
    nmbr_elements_sum = 0
    file_paths = get_file_paths(pickle_directory)
    print(file_paths)
    for path in file_paths:
        print(path)
        comparison_label, df_comparison_values = comparison_series_func(path)
        #  df_mean_values = pd.read_pickle(pickle_directory/(path+'season_aggregation')).sort_index()
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        nmbr_elements_sum += sum(map(lambda df: df.shape[0], df_phases))
        day = pd.Timedelta('1d')
        min_date = min(list(map(lambda df: df.index.min(), df_phases))).date()
        max_date = max(list(map(lambda df: df.index.max(), df_phases))).date()
        print(min_date)
        print(max_date)
        for start_time in pd.date_range(min_date, max_date, freq='d'):
            end_time = start_time + day
            # df_day = df.loc[df.index>start_time and df.index<end_time, :]
            df_phases_day = list(map(lambda df: df.loc[start_time:end_time], df_phases))

            df_comparison_values_day = df_comparison_values.loc[start_time:end_time]
            # print(start_time.date())
            transgression_sum += plot_day(plot_directory, df_phases_day, path.name, str(start_time.date()),
                                          df_comparison_values_day, plot_method, comparison_label)
    return transgression_sum, nmbr_elements_sum


def plot_station_dif_anomalies(pickle_directory, base_plot_directory, anomaly_threshold):
    plot_directory = base_plot_directory / ("StationDif_" + str(anomaly_threshold).replace(".", "_"))

    def plot_station_dif_v2(df_p_day, p_counter):
        transgressions = list(np.where(abs(df_p_day.StationDif) > anomaly_threshold)[0])
        df_p_day.Value.plot(figsize=(24, 6), linewidth=0.9, markevery=transgressions, marker='o',
                            markerfacecolor='black', label="phase" + str(p_counter))
        return len(transgressions)

    def comparison_series_func(station_name):
        return "meanStationAverage", pd.read_pickle(pickle_directory / 'meanStationValues')

    transgression_sum, nmbr_elements_sum = plot_pickle_daywise(pickle_directory, plot_directory, plot_station_dif_v2,
                                                               comparison_series_func)

    print(transgression_sum)
    print(nmbr_elements_sum)
    ratio = transgression_sum / nmbr_elements_sum
    print(ratio)

    f = open(plot_directory / str(ratio), "w+")
    f.close()


def plot_phase_dif_anomalies(pickle_directory, base_plot_directory, anomaly_threshold):
    plot_directory = base_plot_directory / ("PhaseDif_" + str(anomaly_threshold).replace(".", "_"))

    def plot_station_dif_v2(df_p_day, p_counter):
        transgressions = list(np.where(abs(df_p_day.phase_dif) > anomaly_threshold)[0])
        df_p_day.Value.plot(figsize=(24, 6), linewidth=0.9, markevery=transgressions, marker='o',
                            markerfacecolor='black', label="phase" + str(p_counter))
        return len(transgressions)

    def comparison_series_func(station_name):
        return "", pd.DataFrame()

    transgression_sum, nmbr_elements_sum = plot_pickle_daywise(pickle_directory, plot_directory, plot_station_dif_v2,
                                                               comparison_series_func)

    print(transgression_sum)
    print(nmbr_elements_sum)
    ratio = transgression_sum / nmbr_elements_sum
    print(ratio)

    f = open(plot_directory / str(ratio), "w+")
    f.close()


def plot_season_dif_anomalies(pickle_directory, base_plot_directory, anomaly_threshold):
    # anomaly_threshold = 3.2270145810536146

    plot_directory = base_plot_directory / ("SeasDif_" + str(anomaly_threshold).replace(".", "_"))

    def plot_season_dif_v2(df_p_day, p_counter):
        transgressions = list(np.where(abs(df_p_day.SeasDif) > anomaly_threshold)[0])
        df_p_day.Value.plot(figsize=(24, 6), linewidth=0.9, markevery=transgressions, marker='o',
                            markerfacecolor='black', label="phase" + str(p_counter))
        return len(transgressions)

    def comparison_series_func(station_name):
        return "meanSeasonalAverage", pd.read_pickle(
            pickle_directory / (station_name + 'season_aggregation')).sort_index()

    transgression_sum, nmbr_elements_sum = plot_pickle_daywise(pickle_directory, plot_directory, plot_season_dif_v2,
                                                               comparison_series_func)

    print(transgression_sum)
    print(nmbr_elements_sum)
    ratio = transgression_sum / nmbr_elements_sum
    print(ratio)

    f = open(plot_directory / str(ratio), "w+")
    f.close()


def plot_trafo_dif_anomalies(pickle_directory, base_plot_directory):
    anomaly_threshold = 1.5

    plot_directory = base_plot_directory / ("TrafoDif_" + str(anomaly_threshold).replace(".", "_"))

    def plot_trafo_dif_v2(df_p_day, p_counter):
        transgressions = list(np.where(abs(df_p_day.Value.diff()) > anomaly_threshold)[0])
        df_p_day.Value.plot(figsize=(24, 6), linewidth=0.9, markevery=transgressions, marker='o',
                            markerfacecolor='black', label="phase" + str(p_counter))
        return len(transgressions)

    def comparison_series_func(station_name):
        return "", pd.DataFrame()

    transgression_sum, nmbr_elements_sum = plot_pickle_daywise(pickle_directory, plot_directory, plot_trafo_dif_v2,
                                                               comparison_series_func)

    print(transgression_sum)
    print(nmbr_elements_sum)
    ratio = transgression_sum / nmbr_elements_sum
    print(ratio)

    f = open(plot_directory / str(ratio), "w+")
    f.close()


def plot_trafo_dif_anomalies_v2(pickle_directory, base_plot_directory, anomaly_threshold):
    plot_directory = base_plot_directory / ("TrafoDif_v2_" + str(anomaly_threshold).replace(".", "_"))

    def plot_trafo_dif_v2(df_p_day, p_counter):
        transgressions = list(np.where(abs(df_p_day.trafo) > anomaly_threshold)[0])
        df_p_day.Value.plot(figsize=(24, 6), linewidth=0.9, markevery=transgressions, marker='o',
                            markerfacecolor='black', label="phase" + str(p_counter))
        return len(transgressions)

    def comparison_series_func(station_name):
        return "", pd.DataFrame()

    transgression_sum, nmbr_elements_sum = plot_pickle_daywise(pickle_directory, plot_directory, plot_trafo_dif_v2,
                                                               comparison_series_func)

    print(transgression_sum)
    print(nmbr_elements_sum)
    ratio = transgression_sum / nmbr_elements_sum
    print(ratio)

    f = open(plot_directory / str(ratio), "w+")
    f.close()


def plot_time_dif_anomalies(pickle_directory, base_plot_directory, anomaly_threshold):
    plot_directory = base_plot_directory / ("TimeDif_" + str(anomaly_threshold).replace(".", "_"))

    def plot_time_dif_v2(df_p_day, p_counter):
        transgressions = list(np.where(abs(df_p_day.time_passed) > anomaly_threshold)[0])
        df_p_day.Value.plot(figsize=(24, 6), linewidth=0.9, markevery=transgressions, marker='o',
                            markerfacecolor='black', label="phase" + str(p_counter))
        return len(transgressions)

    def comparison_series_func(station_name):
        return "", pd.DataFrame()

    transgression_sum, nmbr_elements_sum = plot_pickle_daywise(pickle_directory, plot_directory, plot_time_dif_v2,
                                                               comparison_series_func)

    print(transgression_sum)
    print(nmbr_elements_sum)
    ratio = transgression_sum / nmbr_elements_sum
    print(ratio)

    f = open(plot_directory / str(ratio), "w+")
    f.close()


def get_quintiles(pickle_directory, quantile):
    file_paths = get_file_paths(pickle_directory)
    print(file_paths)
    aggregated_series = pd.Series()
    for path in file_paths:
        print(path)
        path = pickle_directory / Path(path)
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        for df_p in df_phases:
            ser = df_p.time_passed.reset_index(drop=True).abs()
            aggregated_series = aggregated_series.append(ser, ignore_index=True)
    threshold = aggregated_series.quantile(q=quantile)
    print(threshold)
    return threshold


def show_df2(pickle_name, pickle_dir=Path('pickles')):
    path = pickle_dir / pickle_name
    df_phases_h = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
    #  df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p)), ['1', '2', '3']))
    df_p_h = df_phases_h[0][['Value']].rename(columns={'Value': 'p1'}).loc[
             pd.datetime(2017, 4, 16):pd.datetime(2017, 4, 17)]
    df_p_h['p2'] = df_phases_h[1][['Value']].loc[pd.datetime(2017, 4, 16):pd.datetime(2017, 4, 17)]
    df_p_h['p3'] = df_phases_h[2][['Value']].loc[pd.datetime(2017, 4, 16):pd.datetime(2017, 4, 17)]
    df_p_h['t1'] = df_phases_h[0][['trafo']].loc[pd.datetime(2017, 4, 16):pd.datetime(2017, 4, 17)]
    df_p_h['t2'] = df_phases_h[1][['trafo']].loc[pd.datetime(2017, 4, 16):pd.datetime(2017, 4, 17)]
    df_p_h['t3'] = df_phases_h[2][['trafo']].loc[pd.datetime(2017, 4, 16):pd.datetime(2017, 4, 17)]
    df_p_dif = pd.DataFrame()
    df_p_dif['p1'] = df_p_h['p1'].diff() / df_p_h['p1'].index.to_series().diff().dt.total_seconds()
    df_p_dif['p2'] = df_p_h['p2'].diff() / df_p_h['p2'].index.to_series().diff().dt.total_seconds()
    df_p_dif['p3'] = df_p_h['p3'].diff() / df_p_h['p3'].index.to_series().diff().dt.total_seconds()

    df_p_dif_a = df_p_dif.loc[abs(df_p_dif['p1']) >= 0.15].loc[abs(df_p_dif['p2']) >= 0.15].loc[
        abs(df_p_dif['p3']) >= 0.15]
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_p_dif_a)
        print(df_p_h)


def show_df(pickle_name, pickle_dir=Path('pickles')):
    path = pickle_dir / pickle_name
    df_phases_h = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
    #  df_phases = list(map(lambda p: pd.read_pickle(path / ("phase" + p)), ['1', '2', '3']))
    df_p_h = df_phases_h[0][['Value']].rename(columns={'Value': 'p1'}).loc[
             pd.datetime(2017, 8, 7):pd.datetime(2017, 8, 8)]
    df_p_h['p2'] = df_phases_h[1][['Value']].loc[pd.datetime(2017, 8, 7):pd.datetime(2017, 8, 8)]
    df_p_h['p3'] = df_phases_h[2][['Value']].loc[pd.datetime(2017, 8, 7):pd.datetime(2017, 8, 8)]
    df_p_h['t1'] = df_phases_h[0][['trafo']].loc[pd.datetime(2017, 8, 7):pd.datetime(2017, 8, 8)]
    df_p_h['t2'] = df_phases_h[1][['trafo']].loc[pd.datetime(2017, 8, 7):pd.datetime(2017, 8, 8)]
    df_p_h['t3'] = df_phases_h[2][['trafo']].loc[pd.datetime(2017, 8, 7):pd.datetime(2017, 8, 8)]
    df_p_dif = pd.DataFrame()
    df_p_dif['p1'] = df_p_h['p1'].diff() / df_p_h['p1'].index.to_series().diff().dt.total_seconds()
    df_p_dif['p2'] = df_p_h['p2'].diff() / df_p_h['p2'].index.to_series().diff().dt.total_seconds()
    df_p_dif['p3'] = df_p_h['p3'].diff() / df_p_h['p3'].index.to_series().diff().dt.total_seconds()

    df_p_dif_a = df_p_dif.loc[abs(df_p_dif['p1']) >= 0.15].loc[abs(df_p_dif['p2']) >= 0.15].loc[
        abs(df_p_dif['p3']) >= 0.15]
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        # print(df_p_dif_a)
        print(df_p_h[['p1', 'p2', 'p3']])


def construct_overview2():
    file_paths = os.listdir("./../pickles")
    df_ps = []
    for fp in file_paths:
        path = Path("./../pickles") / fp
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        df_ps.append(df_phases)

    df_table = pd.DataFrame(columns=["Messungszeitraum [d]", "MA Median [s]", "MA Mean [s]", "Max U [V]",
                                     "Min U [V]", "Average U [V]"])

    for df_phases in df_ps:
        time_dif = pd.Series()
        voltage = pd.Series()
        for df_p in df_phases:
            time_dif = time_dif.append(df_p['time_passed'], ignore_index=True)
            voltage = voltage.append(df_p["Value"], ignore_index=True)
        med_time_dif = time_dif.median()
        mean_time_dif = time_dif.mean()
        voltage_min = min(voltage)
        voltage_max = max(voltage)
        voltage_mean = voltage.mean()
        length = (df_phases[0].index[-1] - df_phases[0].index[0]).days
        name = df_phases[0]["ServiceDeliveryPoint"][0]
        name = name[-4:]
        df_table = df_table.append(pd.Series(name=name,
                                             data={"MA Median [s]": med_time_dif, "MA Mean [s]":mean_time_dif,
                                                   "Messungszeitraum [d]": length, "Max U [V]":voltage_max,
                                                    "Min U [V]":voltage_min, "Average U [V]":voltage_mean}))
    df_table1 = df_table.copy()
    df_table.index.name = "Station"
    # df_t = df_table.astype("object").copy()
    print("x")


def construct_overview():
    file_paths = os.listdir("./../pickles")
    df_ps = []
    for fp in file_paths:
        path = Path("./../pickles") / fp
        df_phases = list(map(lambda p: pd.read_pickle(path / ("h_phase" + p)), ['1', '2', '3']))
        df_ps.append(df_phases)

    n_p = 0
    df_table = pd.DataFrame(columns=["Datenpunkte", "Sprunga.", "Zeita.", "Phasena.", "Saisona.",
                                     "Stationsa.", "Messungszeitraum [d]", "Messungsabstand [s]"])
    tr, ph, st, se, ti = 0, 0, 0, 0, 0
    for df_phases in df_ps:
        n_tr = 0
        n_ph = 0
        n_st = 0
        n_se = 0
        n_ti = 0
        time_dif = pd.Series()
        n_p_h = 0
        for df_p in df_phases:
            n_tr = n_tr + df_p[abs(df_p['trafo']) > 0.1].shape[0]
            n_ph = n_ph + df_p[abs(df_p['phase_dif']) > 7.34].shape[0]
            n_st = n_st + df_p[abs(df_p['StationDif']) > 8.772].shape[0]
            n_se = n_se + df_p[abs(df_p['SeasDif']) > 5.87].shape[0]
            n_ti = n_ti + df_p[abs(df_p['time_passed']) > 179].shape[0]
            n_p = n_p + df_p.shape[0]
            n_p_h = n_p_h + df_p.shape[0]
            print(n_tr)
            time_dif = time_dif.append(df_p['time_passed'], ignore_index=True)
        med_time_dif = time_dif.median()
        length = (df_phases[0].index[-1] - df_phases[0].index[0]).days
        name = df_phases[0]["ServiceDeliveryPoint"][0]
        name = name[-4:]
        df_table = df_table.append(pd.Series(name=name,
                                             data={"Datenpunkte": n_p_h, "Sprunga.": n_tr, "Zeita.": n_ti,
                                                   "Phasena.": n_ph, "Saisona.": n_se,
                                                   "Stationsa.": n_st, "Messungsabstand [s]": med_time_dif,
                                                   "Messungszeitraum [d]": length}))
        tr, ti, ph, se, st = tr + n_tr, ti + n_ti, ph + n_ph, se + n_se, st + n_st
    df_table1 = df_table.copy()
    df_table.drop(columns=["Messungszeitraum [d]", "Messungsabstand [s]"], inplace=True)
    df_table.index.name = "Station"
    df_table = df_table.append(pd.Series(name="gesamt", data={"Datenpunkte": n_p, "Sprunga.": tr, "Zeita.": ti,
                                                              "Phasena.": ph, "Saisona.": se,
                                                              "Stationsa.": st}))
    df_table = df_table.append(pd.Series(name="anteil", data={"Datenpunkte": n_p / n_p, "Sprunga.": tr / n_p,
                                                              "Zeita.": ti / n_p,
                                                              "Phasena.": ph / n_p, "Saisona.": se / n_p,
                                                              "Stationsa.": st / n_p}))
    df_t = df_table.astype("object").copy()
    df_t.Datenpunkte = df_t.Datenpunkte.astype("int")
    print("x")


def main():
    construct_overview2()

    # pickle_directory = Path("pickles")
    # base_plot_dir = Path("plots")
    # quantile = .999
    # anomaly_threshold = get_quintiles(pickle_directory, quantile)
    # plot_time_dif_anomalies(pickle_directory, base_plot_dir, anomaly_threshold)


    # plot_trafo_dif_anomalies_v2(pickle_directory, base_plot_dir, 0.15)
    # plot_trafo_dif_anomalies_v2(pickle_directory, base_plot_dir, 0.1)
    # show_df('NW00000000000BISMARKSTRASSNV04609', pickle_directory)

# df_table = pd.DataFrame
# ... n_p = 0
# ... for df_phases in df_ps:
# ...     n_tr = 0
# ...     n_ph = 0
# ...     n_st = 0
# ...     n_se = 0
# ...     n_ti = 0
# ...     time_dif = pd.Series()
# ...     for df_p in df_ps:
# ...         n_tr = n_tr + df_p['trafo'] >0.1
# ...         n_ph = n_ph + df_p['phase_dif'] > 7.34
# ...         n_st = n_st + df_p['StationDif'] > 8.772
# ...         n_se = n_se + df_p['SeasDif'] > 8.772
# ...         n_ti = n_ti + df_p['time_passed'] > 179
# ...         n_p = n_p + df_p.shape[0]
# ...         name = df_p["ServiceDeliveryPoint"][0]
# ...         time_dif.append(df_p['time_passed'], ignore_index=True)
# ...     med_time_dif = time_dif.median()
# ...     length = (df_ps[0].index[-1] - df_ps[0].index[0]).days
# ...     df_table.append(pd.Series(name=name),data= {"Sprunganomalien":n_tr,"Zeitanomalien":n_ti,"Phasenanomalien":n_ph, "Saisonanomalien":n_se, "Stationsanomalien":n_st, "Messungsabstand":med_time_dif, "Anzahl Tage":length})


if __name__ == "__main__":
    main()
