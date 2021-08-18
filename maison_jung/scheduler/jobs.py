import printbetter as pb
import schedule
from suntime import Sun
from datetime import timedelta

from .. import server
from ..utils import load_yaml, paths


config = load_yaml(paths['config'])

latitude, longitude = config['location']
sun = Sun(latitude, longitude)

actions = {
    "lampes": server.actions.lampes,
    "stores": server.actions.stores,
    "arrosage": server.actions.arrosage
}

intervals = {
    "every": [lambda: schedule.every().day],
    "monday": [lambda: schedule.every().day],
    "tuesday": [lambda: schedule.every().tuesday],
    "wednesday": [lambda: schedule.every().wednesday],
    "thursday": [lambda: schedule.every().thursday],
    "friday": [lambda: schedule.every().friday],
    "saturday": [lambda: schedule.every().saturday],
    "sunday": [lambda: schedule.every().sunday]
}
intervals = {**intervals,
             "weekdays": [
                 *intervals['monday'],
                 *intervals['tuesday'],
                 *intervals['wednesday'],
                 *intervals['thursday'],
                 *intervals['friday']
             ],
             "weekend": [
                 *intervals['saturday'],
                 *intervals['sunday']
             ]}


def update(schedules):
    """Updates jobs."""
    sun_hours = {
        "sunrise": sun.get_local_sunrise_time(),
        "sunset": sun.get_local_sunset_time()
    }
    for category in actions:
        schedule.clear(category)  # deletes every job
    for interval, jobs in intervals.items():
        for category, tasks in schedules[interval].items():
            if not tasks:  # no task in category
                continue
            tags = [category]
            for task in tasks:
                if not task['enabled']:
                    continue
                time_data = task['time'].split("/")
                if len(time_data) > 1:  # in relation to sunrise or sunset
                    time = sun_hours[time_data[0]] + timedelta(minutes=int(time_data[1]))
                    time = time.strftime("%H:%M")
                    tags.append("sun")
                else:
                    time = time_data[0]
                for job in jobs:
                    job().at(time).do(actions[category], data=task['data'], source="scheduler").tag(*tags)  # adds job to schedule
    pb.info("-> [scheduler] Jobs updated")


def update_sun(schedules):
    """Updates sunrise and sunset jobs execution time."""
    sun_hours = {
        "sunrise": sun.get_local_sunrise_time(),
        "sunset": sun.get_local_sunset_time()
    }
    schedule.clear("sun")  # deletes jobs in relation to sunrise or sunset
    for interval, jobs in intervals.items():
        for category, tasks in schedules[interval].items():
            if not tasks:  # no tasks in category
                continue
            for task in tasks:
                time_data = task['time'].split("/")
                if not task['enabled'] or len(time_data) <= 1:  # verifies that task is enabled and in relation to sunrise or sunset
                    continue
                tags = [category, "sun"]
                time = sun_hours[time_data[0]] + timedelta(minutes=int(time_data[1]))
                time = time.strftime("%H:%M")
                for job in jobs:
                    job().at(time).do(actions[category], data=task['data'], source="scheduler").tag(*tags)  # adds job to schedule
    pb.info(f"-> [scheduler] Updated sun related jobs (sunrise: {sun_hours['sunrise'].strftime('%H:%M')}, sunset: {sun_hours['sunset'].strftime('%H:%M')})")
