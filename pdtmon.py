import astral
import astral.sun
import datetime

otto_coords = {'lat': 38.662644, 'long': -121.527298}
otto_obs = astral.Observer(latitude=otto_coords['lat'], longitude=otto_coords['long'])

otto_sun_yesterday = astral.sun.sun(otto_obs, datetime.datetime.today() - datetime.timedelta(days=1), tzinfo='America/Los_Angeles')
otto_sun_today = astral.sun.sun(otto_obs, datetime.datetime.today(), tzinfo='America/Los_Angeles')
otto_sun_tomorrow = astral.sun.sun(otto_obs, datetime.datetime.today() + datetime.timedelta(days=1), tzinfo='America/Los_Angeles')

day_length_yesterday = otto_sun_yesterday['sunset'] - otto_sun_yesterday['sunrise']
day_length_today = otto_sun_today['sunset'] - otto_sun_today['sunrise']
day_length_tomorrow = otto_sun_tomorrow['sunset'] - otto_sun_tomorrow['sunrise']

print((
    'Today\n'
    f'Dawn:    {otto_sun_today["dawn"]}\n'
    f'Sunrise: {otto_sun_today["sunrise"]}\n'
    f'Noon:    {otto_sun_today["noon"]}\n'
    f'Sunset:  {otto_sun_today["sunset"]}\n'
    f'Dusk:    {otto_sun_today["dusk"]}\n'
    f'yesterday->today: {day_length_today - day_length_yesterday}\n'
    f'today->tomorrow: {day_length_tomorrow - day_length_today}\n'
))