import urllib.error
import matplotlib.pyplot as plt
import pandas as pd
import pyreadr
from DataSetup import import_from_internet
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.io.img_tiles as cimgt


class Location:
    def __init__(self):
        self.stations = []

    def add_station(self, s):
        self.stations.append(s)


class Station:
    def __init__(self, name, loc, site_id, lat, long, stat_type, df=""):
        self.name = name
        self.Location = loc
        self.Location.add_station(self)
        self.ID = site_id
        self.pos = (lat, long)
        self.stat_type = stat_type
        self.df = df
        self.lat = lat
        self.long = long


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


def plot_map(latlongprojection=ccrs.Mercator()):

    extent = [-0.25, 0, 51.45, 51.59]
    request = cimgt.GoogleTiles(style='satellite')
    fig, axs = plt.subplots(ncols=2, figsize=(18, 8), subplot_kw={'projection': request.crs})

    for ax in axs:
        request = cimgt.GoogleTiles(style='satellite')
        gl = ax.gridlines(draw_labels=True, alpha=0.5)
        gl.xlabels_top = gl.ylabels_right = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        ax.set_extent(extent)
        ax.add_image(request, 13, interpolation='spline36')

        request = cimgt.Stamen(style='toner-lines')
        ax.add_image(request, 14, alpha=0.1, interpolation='spline36')
    return fig, axs


def run_main():
    scalar = 8
    latlongprojection = ccrs.Mercator()
    fig, axs = plot_map(latlongprojection)
    London = setup_stations()
    year = 2020
    year2 = 2019
    plot_x, plot_y, plot_1_s, plot_2_s, plot_c, plot_ec, plot_lw = [], [], [], [], [], [], []
    for station in London.stations:
        try:
            df_2020 = pd.read_csv(f'{year}/{station.ID}.csv')
        except FileNotFoundError:
            try:
                df_2020 = import_from_internet(year, station.ID)
                df_2020.to_csv(f'{year}/{station.ID}.csv')
            except urllib.error.HTTPError:
                print(f'{station.ID} {station.name} failed')
                continue

        try:
            df_2019 = pd.read_csv(f'{year2}/{station.ID}.csv')
        except FileNotFoundError:
            try:
                df_2019 = import_from_internet(year2, station.ID)
                df_2019.to_csv(f'{year2}/{station.ID}.csv')
            except urllib.error.HTTPError:
                print(f'{station.ID} {station.name} failed')
                continue
        station.df = df_2020.fillna(0)

        wk_2019, wk_2020 = [], []
        for i in range(29):
            if i <= 9:
                wk_2019.append(f'0{i+1}-04-2019')
                wk_2020.append(f'0{i+1}-04-2020')
            else:
                wk_2019.append(f'{i+1}-04-2019')
                wk_2020.append(f'{i+1}-04-2020')

        val1 = df_2019.loc[df_2019['Date'].isin(wk_2019)]['Nitrogen oxides as nitrogen dioxide'].mean()
        val2 = df_2020.loc[df_2020['Date'].isin(wk_2020)]['Nitrogen oxides as nitrogen dioxide'].mean()
        print(station.ID, val1, val2, station.stat_type)

        if station.ID == 'HORS':
            val2 = val1

        c = 'lime' if station.ID == 'CLL2' else 'red'
        ec = 'blue' if station.stat_type == 'Urban Traffic' else c
        lw = 2
        linew = lw if station.stat_type == 'Urban Traffic' else 1.5

        plot_x.append(station.long)
        plot_y.append(station.lat)
        plot_1_s.append(val1*scalar)
        plot_2_s.append(val2*scalar)
        plot_c.append(c)
        plot_ec.append(ec)
        plot_lw.append(linew)

    # PLOT #
    s0 = axs[0].scatter(plot_x, plot_y, s=plot_1_s, transform=ccrs.PlateCarree(),
                        color=plot_c, alpha=0.6, edgecolors=plot_ec, linewidth=plot_lw)
    axs[0].set_title('2019')
    s1 = axs[1].scatter(plot_x, plot_y, s=plot_2_s, transform=ccrs.PlateCarree(),
                        color=plot_c, alpha=0.6, edgecolors=plot_ec, linewidth=plot_lw)
    axs[1].set_title('2020')

    # LEGEND 1 #
    proxy_plot0 = axs[1].scatter([50, 50], [10, 10], s=[10*scalar, 500*scalar], transform=ccrs.PlateCarree())
    proxy_plot1 = axs[1].scatter([50], [10], s=[100*scalar], transform=ccrs.PlateCarree(), color='red')
    proxy_plot2 = axs[1].scatter([50], [10], s=[100*scalar], transform=ccrs.PlateCarree(), color='red',
                                 edgecolor='blue', linewidth=lw)
    proxy_plot3 = axs[1].scatter([50], [10], s=[100*scalar], transform=ccrs.PlateCarree(), color='lime')
    leg = axs[1].legend([proxy_plot1, proxy_plot2, proxy_plot3],
                        ['Background\nMeasurement', 'Traffic\nMeasurement', 'London\nBloomsbury'],
                        loc='lower left', bbox_to_anchor=(1, 0.1), labelspacing=1.5, frameon=False)
    axs[1].add_artist(leg)
    ticks = [10*scalar, 20*scalar, 50*scalar, 100*scalar]
    ticks2 = [10, 20, 50, 100]
    plt.setp(leg.get_title(), multialignment='center')

    # LEGEND 2 #
    handles, labels = proxy_plot0.legend_elements(prop="sizes", alpha=0.6, num=ticks)
    a = "\n"
    labels = ticks2
    leg2 = plt.legend(handles, labels, loc="upper left",
                      title=fr'Mean April NO$_x${a}concentration{a}($\mu$g m$^-$$^3$)',
                      scatterpoints=2, bbox_to_anchor=(1, 0.9), labelspacing=1.6, frameon=False)
    plt.setp(leg2.get_title(), multialignment='center')

    # DISPLAY #
    fig.tight_layout(rect=(0, 0, 0.97, 1))
    #plt.savefig(f'{year}plot.png', dpi=600)
    plt.show()


if __name__ == '__main__':
    run_main()
