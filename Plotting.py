import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def get_data():
    df = pd.read_csv('AllData.csv', header=0)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y-%m-%d %H:%M:%S')
    return df


def add_extra_info(df):
    df['Weekday'] = df.DateTime.dt.weekday
    df['Season'] = df.DateTime.dt.month % 12 // 3 + 1
    df['Year'] = df.DateTime.dt.year
    df['Hour'] = df.DateTime.dt.hour
    df['Date'] = df.DateTime.dt.date
    df['Month'] = df.DateTime.dt.month
    df['Day'] = df.DateTime.dt.day
    return df


def group_daily_max(main_df, keys):
    out_dfs = []
    for key in keys:
        df = main_df

        max_daily = df.groupby(pd.Grouper(key='DateTime', freq='D'))[key].transform('max')
        df = df[df[key] == max_daily].drop_duplicates(subset=['Date'], keep='first')

        # df = df[df['Hour'] == 12]

        out_dfs.append(df)
    return out_dfs


def split_years(df):
    return [df[df['Year'] == y] for y in df['Year'].unique()]


def days_after_first_monday(df):
    pd.options.mode.chained_assignment = None
    offset = df['Weekday'].iloc[0] - 8
    if offset == -8:
        offset = -1
    df['Offset Day'] = df['Day'] + offset
    print(df[['Day', 'Weekday', 'Offset Day']])

    pd.options.mode.chained_assignment = 'warn'
    return df


def plot1(df):
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8), sharex='all', sharey='all')
    axs = axs.flatten()
    for i, ax in enumerate(axs):
        df2 = df[df['Year'] == i + 2017]
        sns.lineplot(data=df2, x='Hour', y='Sulphur dioxide', hue='Weekday', ax=ax)
        ax.set_ylabel(f'Sulphur Dioxide Concentration (ug/m^3)')
        ax.set_title(f'{i + 2017}')
        if i != 2:
            ax.get_legend().remove()

    fig.suptitle('Hourly concentrations of Sulphur dioxide sorted by year', y=0.99)
    fig.tight_layout()
    plt.savefig('Figure 1.png', dpi=300)


def plot2(df):
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(20, 10), sharex='all')
    axs = axs.flatten()
    values = ['PM10 particulate matter (Hourly measured)', 'PM2.5 particulate matter (Hourly measured)',
              'Ozone', 'Nitrogen oxides as nitrogen dioxide', 'Nitrogen dioxide', 'Sulphur dioxide']
    names = ['PM10', 'PM2.5', 'Ozone', 'NOx', 'NO2', 'Sulfur Dioxide']
    for i, ax in enumerate(axs):
        df_temp = df
        sns.boxplot(data=df_temp, x='Year', y=values[i], ax=ax, showfliers=False, color='#52acc8')
        ax.set_ylabel(f'{names[i]} Concentration (ug/m^3)')
        ax.locator_params(axis='x', nbins=17)
        ax.tick_params(axis='x', rotation=45)
        ax.xaxis.set_tick_params(labelbottom=True)
    fig.tight_layout(pad=2)
    fig.suptitle('Box plots of the concentrations of atmospheric pollutants by year', y=0.99)
    plt.savefig('Figure 2.png', dpi=300)


def plot3(df):
    fig, axs = plt.subplots(ncols=2, figsize=(12, 5))
    sns.lineplot(data=df, x='Year', y='Nitrogen oxides as nitrogen dioxide', hue='Hour', palette='flare', ax=axs[0])

    df2 = df.loc[(df['Hour'] == 3) | (df['Hour'] == 6) | (df['Hour'] == 9) |
                 (df['Hour'] == 12) | (df['Hour'] == 15) | (df['Hour'] == 18)]

    sns.lineplot(data=df2, x='Year', y='Nitrogen oxides as nitrogen dioxide',
                 hue='Hour', hue_norm=(1, 24), palette='flare', ax=axs[1])
    fig.tight_layout()


def plot4(df):
    keys = ['PM2.5 particulate matter (Hourly measured)',
            'PM10 particulate matter (Hourly measured)',
            'Nitrogen oxides as nitrogen dioxide']
    k = ['PM2.5', 'PM10', 'Nitrogen Oxides']
    dfs = group_daily_max(df, keys)
    fig, axs = plt.subplots(nrows=3, figsize=(8, 9), sharex='all')
    for i, df in enumerate(dfs):
        ax = axs[i]
        df = df[df['Month'] == 4]
        df = df[df['Year'] >= 2016]

        dfs = split_years(df)
        for j, year_df in enumerate(dfs):
            days_after_first_monday(year_df)
            ax.plot(year_df['Offset Day'], year_df[keys[i]], label=j+2016)

        ax.set_xlim(0, 28)
        plt.xticks([0, 7, 14, 21, 28])
        ax.set_ylabel(f'{k[i]} conc. (ug/m^3)')
        if i == 0:
            ax.legend()
        if i == 2:
            ax.set_xlabel('Days After the first Monday of April')
    fig.suptitle('Concentration of Atmospheric pollutants at noon from 2018-2022 across April', y=0.97)
    fig.tight_layout()


def main():
    main_df = add_extra_info(get_data())

    plot1(main_df)
    plot2(main_df)

    plt.show()


if __name__ == '__main__':
    main()
