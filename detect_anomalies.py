import logarithmoforecast
import pandas as pd
from pathlib import Path


def create_ml_dataframe(station_name, phase, pickle_dir=Path('pickles')):
    path = pickle_dir / station_name
    df_ml = pd.read_pickle(path / ("h_phase"+str(phase)))
    df_ml.drop(columns=['ServiceDeliveryPoint'])
    print(df_ml)


def main():
    station_name = 'NW000000000000000000000NBSNST0888'
    test_dir = Path('testPickles')
    create_ml_dataframe(station_name, 0, test_dir)


main()