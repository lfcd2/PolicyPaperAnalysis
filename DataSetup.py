import pandas as pd
from os.path import exists


def import_from_internet(year, loc_id='CLL2'):
    df = pd.read_csv(f'https://uk-air.defra.gov.uk/data_files/site_data/{loc_id}_{year}.csv?v=1', header=4)
    df.to_csv(f'{year}.csv')
    return df


def delete_status_and_unit_cols(df):
    for col in df:
        if col[:4] in ['stat', 'unit']:
            df.drop(col, axis=1, inplace=True)
    return df


def get_data():
    df_list = []
    for year in range(1992, 2024):
        if exists(f'{year}.csv'):
            df = pd.read_csv(f'{year}.csv', header=0)
            print(f'Data for {year} retrieved from cache')
        else:
            df = import_from_internet(year)
            print(f'Data for {year} retrieved from internet')

        df = delete_status_and_unit_cols(df)

        df_list.append(df)

    dataframe = pd.concat(df_list, ignore_index=True)
    for col in dataframe:
        if col == 'Unnamed: 0':
            dataframe.pop('Unnamed: 0')

    print('Data combined')
    return dataframe


def fix_times(df):
    pd.options.mode.chained_assignment = None
    date = df.pop('Date')
    time = df.pop('time')
    for index, value in enumerate(time):
        if value == '24:00':
            time[index] = '23:59'
    df['DateTime'] = pd.to_datetime(date + ' ' + time, format='%d-%m-%Y %H:%M')
    pd.options.mode.chained_assignment = 'warn'

    print('Date and Time converted to datetime object')
    return df


def cache_dataframe(df):
    df.to_csv('AllData.csv')
    print('Dataframe cached')


def fix_labels(df):
    df['PM2.5 particulate matter (Hourly measured)'] = df['PM2.5 particulate matter (Hourly measured)'].fillna(
        df['PM<sub>2.5</sub> particulate matter (Hourly measured)'])
    df.pop('PM<sub>2.5</sub> particulate matter (Hourly measured)')
    df['PM10 particulate matter (Hourly measured)'] = df['PM10 particulate matter (Hourly measured)'].fillna(
        df['PM<sub>10</sub> particulate matter (Hourly measured)'])
    df.pop('PM<sub>10</sub> particulate matter (Hourly measured)')
    for col in ['PM10 particulate matter (Hourly measured)', 'PM2.5 particulate matter (Hourly measured)', 'Ozone',
                'Nitrogen oxides as nitrogen dioxide', 'Nitrogen dioxide', 'Sulphur dioxide']:
        df.loc[df[col] < 0, col] = 0

    return df


def main():
    main_df = fix_labels(fix_times(get_data()))

    cache_dataframe(main_df)


if __name__ == '__main__':
    main()
