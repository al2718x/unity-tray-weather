#!/usr/bin/env python3

import datetime
import os
import requests
import subprocess
import gi.repository
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import AppIndicator3


class MyIndicator:
    def __init__(self):
        # noinspection PyArgumentList
        self.ind = AppIndicator3.Indicator.new(
            'Weather Indicator 1.0.0',
            'weather-severe-alert',
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.menu = Gtk.Menu()

        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.menu_item('Forecast', 'weather-clear', dir_path + '/run.sh')
        self.menu_item('Quit', 'application-exit')

        self.menu.show_all()
        self.ind.set_menu(self.menu)

    @staticmethod
    def weather_icon(code):
        icons = {
            113: 'weather-clear',               # Sunny / Clear

            116: 'weather-few-clouds',          # Partly cloudy
            119: 'weather-few-clouds',          # Cloudy

            122: 'weather-overcast',            # Overcast

            143: 'weather-fog',                 # Mist
            248: 'weather-fog',                 # Fog
            260: 'weather-fog',                 # Freezing fog

            176: 'weather-showers-scattered',   # Patchy rain possible
            293: 'weather-showers-scattered',   # Patchy light rain
            296: 'weather-showers-scattered',   # Light rain
            299: 'weather-showers-scattered',   # Moderate rain at times
            302: 'weather-showers-scattered',   # Moderate rain
            311: 'weather-showers-scattered',   # Light freezing rain

            305: 'weather-showers',             # Heavy rain at times
            308: 'weather-showers',             # Heavy rain

            179: 'weather-snow',                # Patchy snow possible
            182: 'weather-snow',                # Patchy sleet possible

            227: 'weather-snow',                # Blowing snow
            230: 'weather-snow',                # Blizzard
            185: 'weather-snow',                # Patchy freezing drizzle possible
            263: 'weather-snow',                # Patchy light drizzle
            266: 'weather-snow',                # Light drizzle
            281: 'weather-snow',                # Freezing drizzle
            284: 'weather-snow',                # Heavy freezing drizzle

            200: 'weather-storm',               # Thundery outbreaks possible
        }
        icon = icons.get(code, 'weather-severe-alert')

        now = datetime.datetime.now()
        hour = int(now.strftime('%H'))
        if 8 < hour < 20:
            pass
        else:  # night
            if 113 == code:
                icon = 'weather-clear-night'
            if 116 == code:
                icon = 'weather-few-clouds-night'
            if 119 == code:
                icon = 'weather-few-clouds-night'

        return icon

    def update(self):
        temp_str = ''
        weather_code = 0
        try:
            r = requests.get('https://wttr.in/Tokyo?format=j1')
            data = r.json()
            data_current = data['current_condition'][0]
            temp = int(data_current['temp_C'])
            temp_str = str(temp)
            if temp > 0:
                temp_str = '+' + temp_str
            weather_code = int(data_current['weatherCode'])
            weather_value = data_current['weatherDesc'][0]['value']
            print(temp_str, weather_code, weather_value)
        except Exception:
            pass
        self.ind.set_icon(self.weather_icon(weather_code))
        self.ind.set_label(temp_str, '')
        GLib.timeout_add_seconds(300, self.update)

    def menu_item(self, label, icon_name, connect_args=None):
        item = Gtk.ImageMenuItem()
        img = Gtk.Image()
        img.set_from_icon_name(icon_name, 16)
        item.set_image(img)
        item.set_always_show_image(True)
        item.set_label(label)
        if connect_args:
            item.connect('activate', self.run, connect_args)
        else:
            item.connect('activate', self.quit)
        self.menu.append(item)

    def main(self):
        self.update()
        Gtk.main()

    def run(self, widget, param):
        subprocess.Popen(param)

    def quit(self, widget):
        Gtk.main_quit()


if __name__ == '__main__':
    indicator = MyIndicator()
    indicator.main()

