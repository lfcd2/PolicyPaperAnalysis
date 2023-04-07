import urllib.error

import pyreadr
from DataSetup import import_from_internet


class Location:
    def __init__(self):
        self.stations = []

    def add_station(self, s):
        self.stations.append(s)


class Station:
    def __init__(self, name, loc, site_id, lat, long, stat_type):
        self.name = name
        self.Location = loc
        self.Location.add_station(self)
        self.ID = site_id
        self.pos = (lat, long)
        self.stat_type = stat_type


def get_london_nox():
    df = pyreadr.read_r('AURN_metadata.RData')['AURN_metadata']
    df.drop(df['Greater London' != df['zone']].index, inplace=True)
    parameter = 'NOXasNO2'
    df.drop(df[parameter != df['parameter']].index, inplace=True)
    df.drop(df['ongoing' != df['end_date']].index, inplace=True)
    df.to_csv('codes.csv')
    return df


def setup_stations():
    df = get_london_nox()
    London = Location()
    for index, row in df.iterrows():
        Station(row['site_name'], London, row['site_id'], row['latitude'], row['longitude'], row['location_type'])
    return London


def run_main():
    London = setup_stations()

    for station in London.stations:
        try:
            df = import_from_internet(2020, station.ID)
            print(f'{station.ID} {station.name} succeeded to retrieve data')
        except urllib.error.HTTPError:
            print(f'{station.ID} {station.name} failed')


if __name__ == '__main__':
    run_main()


