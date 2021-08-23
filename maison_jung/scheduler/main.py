import printbetter as pb
import schedule
import threading, time  # for run_continuously

from . import jobs
from ..utils import load_yaml, paths


schedules = load_yaml(paths["schedules"])


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



def file_check():
    """Update jobs if schedules were modified."""
    global schedules
    new_schedules = load_yaml(paths["schedules"])
    if schedules != new_schedules:
        pb.info("<- [scheduler] Schedules file changed")
        schedules = new_schedules
        jobs.update(schedules)


def start():
    jobs.update(schedules)
    schedule.every(1).minutes.do(file_check)
    schedule.every().day.at("13:00").do(jobs.update_sun, schedules)
    run_continuously()  # starts schedule thread
