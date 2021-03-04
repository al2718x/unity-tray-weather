#!/usr/bin/env python3

import datetime
import locale
import os
import sys
import requests
import subprocess
import gi.repository
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import AppIndicator3


class MyIndicator:
    timeout = 300
    timeout_id = 0

    def __init__(self):
        # noinspection PyArgumentList
        self.ind = AppIndicator3.Indicator.new(
            'Weather Indicator 1.1.1',
            'weather-severe-alert',
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.menu = Gtk.Menu()

        wttr = os.path.dirname(os.path.realpath(__file__)) + '/wttr.sh'

        self.menu_item('Weather Forecast', 'weather-clear', self.run, [wttr, '125x40', sys.argv[1] + '?lang=' + sys.argv[2]])
        self.menu_item('Moon Phase', 'weather-clear-night', self.run, [wttr, '73x27', 'Moon?lang=' + sys.argv[2]])
        self.menu_item('Refresh', 'emblem-synchronizing', self.refresh)
        self.menu_item('Quit', 'application-exit', self.quit)

        self.menu.show_all()
        self.ind.set_menu(self.menu)

    def menu_item(self, label, icon_name, action, args=None):
        item = Gtk.ImageMenuItem()
        img = Gtk.Image()
        img.set_from_icon_name(icon_name, 16)
        item.set_image(img)
        item.set_always_show_image(True)
        item.set_label(label)
        if args:
            item.connect('activate', action, args)
        else:
            item.connect('activate', action)
        self.menu.append(item)

    @staticmethod
    def weather_icon(code, is_day):
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

            314: 'weather-snow',                # LightSleet
            317: 'weather-snow',                # LightSleet
            320: 'weather-snow',                # LightSnow
            323: 'weather-snow',                # LightSnowShowers
            326: 'weather-snow',                # LightSnowShowers
            329: 'weather-snow',                # HeavySnow
            332: 'weather-snow',                # HeavySnow
            335: 'weather-snow',                # HeavySnowShowers
            338: 'weather-snow',                # HeavySnow
            350: 'weather-snow',                # LightSleet
            353: 'weather-showers-scattered',   # LightShowers
            356: 'weather-showers',             # HeavyShowers
            359: 'weather-showers',             # HeavyRain
            362: 'weather-snow',                # LightSleetShowers
            365: 'weather-snow',                # LightSleetShowers
            368: 'weather-snow',                # LightSnowShowers
            371: 'weather-snow',                # HeavySnowShowers
            374: 'weather-snow',                # LightSleetShowers
            377: 'weather-snow',                # LightSleet
            386: 'weather-snow',                # ThunderyShowers
            389: 'weather-storm',               # ThunderyHeavyRain
            392: 'weather-snow',                # ThunderySnowShowers
            395: 'weather-snow',                # HeavySnowShowers
        }
        icon = icons.get(code, 'weather-severe-alert')

        if not is_day:
            if 113 == code:
                icon = 'weather-clear-night'
            if 116 == code:
                icon = 'weather-few-clouds-night'
            if 119 == code:
                icon = 'weather-few-clouds-night'

        return icon

    @staticmethod
    def is_day(t_from, t_till):
        current_locale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, 'en_US.utf8')
        is_day = False
        now = datetime.datetime.now()
        try:
            d_from = datetime.datetime.strptime(t_from.strip(), '%I:%M %p')
            d_till = datetime.datetime.strptime(t_till.strip(), '%I:%M %p')
            t_now = now.strftime('%H:%M')
            d_now = datetime.datetime.strptime(t_now, '%H:%M')
            if d_from < d_now < d_till:
                is_day = True
        except Exception as e:
            print(e)
            if 8 < int(now.strftime('%H')) < 20:
                is_day = True
        locale.setlocale(locale.LC_TIME, current_locale)
        return is_day

    def update(self):
        temp_str = ''
        weather_code = 0
        is_day = True
        try:
            r = requests.get('https://wttr.in/' + sys.argv[1] + '?format=j1')
            data = r.json()
            data_current = data['current_condition'][0]
            temp = int(data_current['temp_C'])
            temp_str = str(temp)
            if temp > 0:
                temp_str = '+' + temp_str
            weather_code = int(data_current['weatherCode'])
            weather_value = data_current['weatherDesc'][0]['value']
            astronomy = data['weather'][0]['astronomy'][0]
            sunrise = astronomy['sunrise']
            sunset = astronomy['sunset']
            is_day = self.is_day(sunrise, sunset)
            print(temp_str, weather_code, weather_value, sunrise, '-', sunset, 'day=', is_day)
        except Exception as e:
            print(e)
        if 0 == weather_code:
            self.timeout = 30
        else:
            self.timeout = 300
        self.ind.set_icon(self.weather_icon(weather_code, is_day))
        self.ind.set_label(temp_str, '')
        self.timeout_id = GLib.timeout_add_seconds(self.timeout, self.update)

    def refresh(self, widget):
        try:
            GLib.source_remove(self.timeout_id)
        except Exception as e:
            print(e)
        self.update()

    def run(self, widget, param):
        subprocess.Popen(param)

    def quit(self, widget):
        Gtk.main_quit()

    def main(self):
        self.update()
        Gtk.main()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Use:', 'weather.py', '[city]', '[language]')
        quit()
    indicator = MyIndicator()
    indicator.main()
