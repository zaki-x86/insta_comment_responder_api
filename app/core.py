import os
from decouple import config

from app.service import FBBService

from apscheduler.schedulers.background import BackgroundScheduler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class AppState:
    def __init__(self):
        self.base_path = BASE_DIR
        self.monitor = []
        self.fbb = FBBService(
            access_token=config("META_DEVELOPER_ACCESS_TOKEN"),
            insta_account=config("INSTAGRAM_ACCOUNT_ID"),
        )
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.reset_monitor, "interval", minutes=15)

    def reset_monitor(self):
        self.monitor = []

state = AppState()

def get_monitor_state() -> AppState:
    global state
    return state.monitor
