import astral
import astral.sun
import datetime
import pytz
import ephem

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock

'''
otto_coords = {'lat': 38.662644, 'long': -121.527298}
otto_obs = astral.Observer(latitude=otto_coords['lat'], longitude=otto_coords['long'])

otto_sun_yesterday = astral.sun.sun(otto_obs, datetime.datetime.today() - datetime.timedelta(days=1), tzinfo='America/Los_Angeles')
otto_sun_today = astral.sun.sun(otto_obs, datetime.datetime.today(), tzinfo='America/Los_Angeles')
otto_sun_tomorrow = astral.sun.sun(otto_obs, datetime.datetime.today() + datetime.timedelta(days=1), tzinfo='America/Los_Angeles')

day_length_yesterday = otto_sun_yesterday['sunset'] - otto_sun_yesterday['sunrise']
day_length_today = otto_sun_today['sunset'] - otto_sun_today['sunrise']
day_length_tomorrow = otto_sun_tomorrow['sunset'] - otto_sun_tomorrow['sunrise']
temp_neg_td = datetime.timedelta(days=-1, seconds=30000)
'''

'''The astral library has info from NOAA to 2099
the daylight savings "utc_transition dates" from pytz only go to 2037 :(
'''


class screen(Widget):
    # all of the variables that the ui pulls data from
    alpha = NumericProperty()
    otto_info = {'lat': 38.662644, 'long': -121.527298, 'tz':'US/Pacific'}
    otto_obs = astral.Observer(latitude=otto_info['lat'], longitude=otto_info['long'])

    day_length_yesterday_str = StringProperty()
    day_length_today_str = StringProperty()
    day_length_tomorrow_str = StringProperty()
    yesterday_today_delta_str = StringProperty()
    today_tomorrow_delta_str = StringProperty()
    date = StringProperty()
    current_time = StringProperty()

    day_transition_1 = StringProperty()
    day_transition_2 = StringProperty()

    pdt_or_pst_completion_str = StringProperty()
    year_transition_1 = StringProperty()
    year_transition_2 = StringProperty()

    # update all of the numbers that change by-the-minute
    def update_minute_info(self):
        # current time, used in many of following calculations
        rn = datetime.datetime.now(tz=pytz.timezone(self.otto_info['tz']))
        self.current_time = rn.strftime('%H:%M')

        # update alpha brightness according to time of day
        if rn.time() < datetime.time(6):
            self.alpha = 0.25
        elif rn.time() < datetime.time(22):
            self.alpha = 0.80
        else:
            self.alpha = 0.25

        # TODO: change references from datetime.datetime.today() to rn
        otto_sun_today = astral.sun.sun(self.otto_obs, rn, tzinfo=self.otto_info['tz'])
        otto_sun_tomorrow = astral.sun.sun(self.otto_obs, rn + datetime.timedelta(days=1), tzinfo=self.otto_info['tz'])

        # find next 2 important daily transitions
        if rn < otto_sun_today['dawn']:  # rn before today.dawn
            #transitions are today.dawn, today.dusk
            self.day_transition_1 = f'dawn {otto_sun_today["dawn"].strftime("%H:%M")}'
            self.ids.lbl_daymom_tom_1.color = (1,1,0,0)
            self.day_transition_2 = f'dusk {otto_sun_today["dusk"].strftime("%H:%M")}'
            self.ids.lbl_daymom_tom_2.color = (1,1,0,0)
        elif rn < otto_sun_today['dusk']:  # rn before today.dusk:
            # transitions are today.dusk, tomorrow.dawn
            self.day_transition_1 = f'dusk {otto_sun_today["dusk"].strftime("%H:%M")}'
            self.ids.lbl_daymom_tom_1.color = (1,1,0,0)
            self.day_transition_2 = f'dawn {otto_sun_tomorrow["dawn"].strftime("%H:%M")}'
            self.ids.lbl_daymom_tom_2.color = (1,1,0,self.alpha)
        else:
            # transitions are tomorrow.dawn, tomorrow.dusk
            self.day_transition_1 = f'dawn {otto_sun_tomorrow["dawn"].strftime("%H:%M")}'
            self.ids.lbl_daymom_tom_1.color = (1,1,0,self.alpha)
            self.day_transition_2 = f'dusk {otto_sun_tomorrow["dusk"].strftime("%H:%M")}'
            self.ids.lbl_daymom_tom_2.color = (1,1,0,self.alpha)

    # update all of the numbers that change once per day
    def update_daily_info(self):
        # current time, used in many of following calculations
        rn = datetime.datetime.now(tz=pytz.timezone(self.otto_info['tz']))

        # get sun times for 3 days
        otto_sun_yesterday = astral.sun.sun(self.otto_obs, datetime.datetime.today() - datetime.timedelta(days=1), tzinfo=self.otto_info['tz'])
        otto_sun_today = astral.sun.sun(self.otto_obs, datetime.datetime.today(), tzinfo=self.otto_info['tz'])
        otto_sun_tomorrow = astral.sun.sun(self.otto_obs, datetime.datetime.today() + datetime.timedelta(days=1), tzinfo=self.otto_info['tz'])

        # compute day lengths
        day_length_yesterday = otto_sun_yesterday['sunset'] - otto_sun_yesterday['sunrise']
        self.day_length_yesterday_str = self.daylen_tostr(day_length_yesterday)
        day_length_today = otto_sun_today['sunset'] - otto_sun_today['sunrise']
        self.day_length_today_str = self.daylen_tostr(day_length_today)
        day_length_tomorrow = otto_sun_tomorrow['sunset'] - otto_sun_tomorrow['sunrise']
        self.day_length_tomorrow_str = self.daylen_tostr(day_length_tomorrow)

        # compute how much longer today was vs yesterday, change delta text color
        self.yesterday_today_delta_str = self.daydelta_tostr(day_length_today - day_length_yesterday)
        if self.yesterday_today_delta_str[1] == '+':
            self.ids.yest_delta.color = (0,1,0,self.alpha)
        else:
            self.ids.yest_delta.color = (1,0,0,self.alpha)

        # compute how much longer tomorrow will be vs today, change delta text color
        self.today_tomorrow_delta_str = self.daydelta_tostr(day_length_tomorrow - day_length_today)
        if self.today_tomorrow_delta_str[1] == '+':
            self.ids.tom_delta.color = (0,1,0,self.alpha)
        else:
            self.ids.tom_delta.color = (1,0,0,self.alpha)

        # update today's date
        self.date = rn.strftime('%Y.%m.%d')

        # compute PST or PDT completion percentage
        daylight_trans_dates = [x.date() for x in pytz.timezone('US/Pacific')._utc_transition_times
                                if x.year>=rn.year-1 and x.year<=rn.year+1]  # has daylight times last year to next year
        if rn.date() < daylight_trans_dates[2]: # before this year's spring forward)
            # useful dates are last year's fall back and this year's spring forward. currently PST
            pst_duration_days = daylight_trans_dates[2] - daylight_trans_dates[1]
            pst_completed_days = rn.date() - daylight_trans_dates[1]
            self.pdt_or_pst_completion_str = f'PST is {pst_completed_days/pst_duration_days*100:.2f}% done.'
        elif rn.date() < daylight_trans_dates[3]: # between [spring forward and fall back)
            # useful dates: this year's spring forward, fall back. currently PDT :)
            pdt_duration_days = daylight_trans_dates[3] - daylight_trans_dates[2]
            pdt_completed_days = rn.date() - daylight_trans_dates[2]
            self.pdt_or_pst_completion_str = f'PDT is {pdt_completed_days/pdt_duration_days*100:.2f}% done.'
        else:  # you're after this year's fall back]
            # useful dates: this year's fall back, next year's spring forward. currently PST
            pst_duration_days = daylight_trans_dates[4] - daylight_trans_dates[3]
            pst_completed_days = rn.date() - daylight_trans_dates[3]
            self.pdt_or_pst_completion_str = f'PST is {pst_completed_days/pst_duration_days*100:.2f}% done.'

        # find next 2 important yearly transitions. include time changes, equinoxes, solstices
        year_transitions = [['spring forward', daylight_trans_dates[2]], ['fall back', daylight_trans_dates[3]]]
        year_transitions.append(['spring equinox', ephem.next_spring_equinox(str(rn.year)).datetime().date()])
        year_transitions.append(['summer solstice', ephem.next_summer_solstice(str(rn.year)).datetime().date()])
        year_transitions.append(['fall equinox', ephem.next_fall_equinox(str(rn.year)).datetime().date()])
        year_transitions.append(['winter solstice', ephem.next_winter_solstice(str(rn.year)).datetime().date()])
        year_transitions.append(['spring forward', daylight_trans_dates[4]])
        year_transitions.append(['spring equinox', ephem.next_spring_equinox(str(rn.year+1)).datetime().date()])
        # sort the transitions. (are these astronomical events always guaranteed to be in the same order?)
        year_transitions.sort(key=lambda x: x[1])
        year_transitions = [x for x in year_transitions if rn.date() <= x[1]]
        self.year_transition_1 = f'{year_transitions[0][0]}  {year_transitions[0][1].strftime("%Y.%m.%d")}  ' \
                                 f'Δ{(year_transitions[0][1] - rn.date()).days}d'
        self.year_transition_2 = f'{year_transitions[1][0]}  {year_transitions[1][1].strftime("%Y.%m.%d")}  ' \
                                 f'Δ{(year_transitions[1][1] - rn.date()).days}d'

    def daylen_tostr(self, td):
        rtn = f'{td.seconds // 3600:02}h ' \
              f'{(td.seconds % 3600) // 60:02}m ' \
              f'{(td.seconds % 60):02}s'
        return rtn

    def daydelta_tostr(self, td):
        rtn = 'Δ'
        if td < datetime.timedelta():
            td = -td
            rtn += '-'
        else:
            rtn += '+'
        rtn += f'{(td.seconds % 3600) // 60:02}m:' \
               f'{(td.seconds % 60):02}s'
        return rtn

class pdtmonApp(App):
    def build(self):
        rtn = screen()
        rtn.update_minute_info()
        Clock.schedule_interval(lambda dt: rtn.update_minute_info(), 5)  # update every 5 sec for a somewhat reliable thing
        rtn.update_daily_info()
        Clock.schedule_interval(lambda dt: rtn.update_daily_info(), 60 * 10)  # update every 10 min. randomly chosen
        return rtn

if __name__ == '__main__':
    Config.set('graphics', 'width', '1024')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'show_cursor', 0)
    #Config.set('graphics', 'fullscreen', 1)
    pdtmonApp().run()