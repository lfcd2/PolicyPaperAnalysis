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
    def __init__(self, name, loc, site_id, lat, long, stat_type, pollutant, df=""):
        self.name = name
        self.Location = loc
        self.Location.add_station(self)
        self.ID = site_id
        self.pos = (lat, long)
        self.stat_type = stat_type
        self.parameter = pollutant
        self.df = df
        self.lat = lat
        self.long = long


def get_london_nox():
    df = pyreadr.read_r('AURN_metadata.RData')['AURN_metadata']
    df.drop(df['Greater London' != df['zone']].index, inplace=True)
    parameter = 'NOXasNO2'
    parameters = ['NOXasNO2', 'PM2.5']
    df = df.loc[df['parameter'].isin(parameters)]
    #df.drop(df[parameter != df['parameter']].index, inplace=True)
    df.drop(df['ongoing' != df['end_date']].index, inplace=True)
    df.to_csv('codes.csv')
    return df


def setup_stations():
    df = get_london_nox()
    London = Location()
    for index, row in df.iterrows():
        Station(row['site_name'], London, row['site_id'], row['latitude'], row['longitude'], row['location_type'], row['parameter'],)
    return London


def plot_map(latlongprojection=ccrs.Mercator()):

    extent = [-0.22, -0.12, 51.49, 51.55]
    request = cimgt.GoogleTiles(style='satellite')
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(20, 8), subplot_kw={'projection': request.crs})
    axs = axs.flatten()
    for i, ax in enumerate(axs):

        gl = ax.gridlines(draw_labels=True, alpha=0.5)
        gl.xlabels_top = gl.ylabels_right = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        ax.set_extent(extent)

        request = cimgt.Stamen(style='terrain')
        ax.add_image(request, 14, interpolation='spline36')

        #request = cimgt.GoogleTiles(style='satellite')
        #ax.add_image(request, 13, alpha=0.2, interpolation='spline36')

    return fig, axs


def run_main():
    scalar = 10
    latlongprojection = ccrs.Mercator()
    fig, axs = plot_map(latlongprojection)
    London = setup_stations()
    year = 2020
    year2 = 2019
    plot_x, plot_y, plot_1_s, plot_2_s, plot_3_s, plot_4_s, plot_c, plot_ec, plot_lw = [], [], [], [], [], [], [], [], []
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

        try:
            val1 = df_2019['Nitrogen oxides as nitrogen dioxide'].median()
            val2 = df_2020['Nitrogen oxides as nitrogen dioxide'].median() # .loc[df_2020['Date'].isin(wk_2020)]
        except KeyError:
            val1, val2 = 0, 0
        print(station.ID, val1, val2, station.stat_type)
        try:
            val3 = df_2019['PM<sub>2.5</sub> particulate matter (Hourly measured)'].median()
            val4 = df_2020['PM<sub>2.5</sub> particulate matter (Hourly measured)'].median()
        except KeyError:
            val3, val4 = 0, 0

        if station.ID == 'HORS':
            val2 = val1

        c = 'lime' if station.ID == 'CLL2' else 'red'
        if station.stat_type == "Urban Traffic":
            c = 'blue'
        ec = 'blue' if station.stat_type == 'Urban Traffic' else c

        plot_x.append(station.long)
        plot_y.append(station.lat)
        plot_1_s.append(val1*scalar)
        plot_2_s.append(val2*scalar)
        plot_3_s.append(val3 * scalar)
        plot_4_s.append(val4 * scalar)
        plot_c.append(c)
        plot_ec.append(ec)

    # PLOT #
    print(plot_1_s, plot_2_s, plot_3_s, plot_4_s)
    s0 = axs[0].scatter(plot_x, plot_y, s=plot_1_s, transform=ccrs.PlateCarree(),
                        color=plot_c, alpha=0.3, edgecolors=plot_ec)
    axs[0].set_title(r'April 2019 NO$_x$')
    s1 = axs[1].scatter(plot_x, plot_y, s=plot_2_s, transform=ccrs.PlateCarree(),
                        color=plot_c, alpha=0.3, edgecolors=plot_ec)
    axs[1].set_title(r'April 2020 NO$_x$')
    s2 = axs[2].scatter(plot_x, plot_y, s=plot_3_s, transform=ccrs.PlateCarree(),
                        color=plot_c, alpha=0.3, edgecolors=plot_ec)
    axs[2].set_title(r'April 2019 PM$_{2.5}$')
    s3 = axs[3].scatter(plot_x, plot_y, s=plot_4_s, transform=ccrs.PlateCarree(),
                        color=plot_c, alpha=0.3, edgecolors=plot_ec)
    axs[3].set_title(r'April 2020 PM$_{2.5}$')


    # LEGEND 1 #
    proxy_plot0 = axs[1].scatter([50, 50], [10, 10], s=[10*scalar, 500*scalar], transform=ccrs.PlateCarree())
    proxy_plot1 = axs[1].scatter([50], [10], s=[100*scalar], transform=ccrs.PlateCarree(), color='red')
    proxy_plot2 = axs[1].scatter([50], [10], s=[100*scalar], transform=ccrs.PlateCarree(), color='blue',
                                 edgecolor='blue')
    proxy_plot3 = axs[1].scatter([50], [10], s=[100*scalar], transform=ccrs.PlateCarree(), color='lime')
    leg = axs[1].legend([proxy_plot1, proxy_plot2, proxy_plot3],
                        ['Background\nMeasurement', 'Traffic\nMeasurement', 'London\nBloomsbury'],
                        loc='lower left', bbox_to_anchor=(1.05, 0.01), labelspacing=1.5, frameon=False)
    axs[1].add_artist(leg)
    ticks = [10*scalar, 20*scalar, 50*scalar, 100*scalar]
    ticks2 = [10, 20, 50, 100]
    plt.setp(leg.get_title(), multialignment='center')

    # LEGEND 2 #
    handles, labels = proxy_plot0.legend_elements(prop="sizes", alpha=0.6, num=ticks)
    a = "\n"
    labels = ticks2
    leg2 = plt.legend(handles, labels, loc="upper left",
                      title=fr'Mean concentration{a}($\mu$g m$^-$$^3$)',
                      scatterpoints=2, bbox_to_anchor=(1.05, 0.99), labelspacing=1.9, frameon=False)
    plt.setp(leg2.get_title(), multialignment='center')

    # DISPLAY #
    fig.tight_layout(rect=(0.18, 0, 0.82, 1))
    plt.savefig(f'{year}plot4(both).png', dpi=1200)
    plt.show()


if __name__ == '__main__':
    run_main()
