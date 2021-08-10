import schedule
import threading, time  # for run_continuously
from suntime import Sun
from datetime import timedelta
import server.actions
from server import pb  # import printbetter from __init__.py
from server.utils import loadYaml
# TODO logging

schedules = loadYaml("schedules")
config = loadYaml("config")

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


# From https://schedule.readthedocs.io/en/stable/background-execution.html
def run_continuously(interval=1):
    """
    Continuously run, while executing pending jobs at each elapsed time interval.
    @return cease_continuous_run: threading. Event which can be set to cease continuous run.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def fileCheck():
    """Calls `updateJobs` if schedules were modified."""
    global schedules
    newSchedules = loadYaml("schedules")
    if schedules != newSchedules:
        pb.info("<- [scheduler] Schedules file changed")
        schedules = newSchedules
        updateJobs()


def updateJobs():
    """Updates jobs based on schedules file."""
    sunHours = {
        "sunrise": sun.get_local_sunrise_time(),
        "sunset": sun.get_local_sunset_time()
    }
    for category in actions.keys():
        schedule.clear(category)  # deletes every job
    for interval, jobs in intervals.items():
        for category, tasks in schedules[interval].items():
            if not tasks:  # no tasks in category
                continue
            for task in tasks:
                if not task['enabled']:
                    continue
                timeData = task['time'].split('/')
                tags = [category]
                if len(timeData) > 1:  # in relation to sunrise or sunset
                    time = sunHours[timeData[0]] + timedelta(minutes=int(timeData[1]))
                    time = time.strftime('%H:%M')
                    tags.append('sun')
                else:
                    time = timeData[0]
                for job in jobs:
                    job().at(time).do(actions[category], data=task['data'], source="scheduler").tag(*tags)  # adds job to schedule
    pb.info("-> [scheduler] Jobs updated")


def updateSunJobs():
    """Updates sunrise and sunset jobs execution time."""
    sunHours = {
        "sunrise": sun.get_local_sunrise_time(),
        "sunset": sun.get_local_sunset_time()
    }
    schedule.clear("sun")  # deletes jobs in relation to sunrise or sunset
    for interval, jobs in intervals:
        for category, tasks in schedules[interval]:
            for task in tasks:
                timeData = task['time'].split('/')
                if not task['enabled'] or len(time) > 1:  # checks that task is enabled and in relation to sunrise or sunset
                    continue
                tags = [category]
                time = sunHours[timeData[0]] + timedelta(minutes=int(timeData[1]))
                time = time.strftime('%H:%M')
                tags.append('sun')
                for job in jobs():
                    job.at(time).do(actions[category], data=task['data'], source="scheduler").tags(*tags)  # adds job to schedule
    pb.info(f"-> [scheduler] Updated sun related jobs (sunrise: {sunHours['sunrise'].strftime('%H:%M')}, sunset: {sunHours['sunset'].strftime('%H:%M')})")


def main():
    updateJobs()
    schedule.every(1).minutes.do(fileCheck)
    schedule.every().day.at("13:00").do(updateSunJobs)
    run_continuously()  # starts schedule thread
