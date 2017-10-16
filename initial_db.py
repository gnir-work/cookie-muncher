import datetime

from db import MuncherSchedule, MuncherConfig, engine
from sqlalchemy.orm import Session
import json

DEFAULT_DEPTH = 1
DEFAULT_LOG_FOLDER = "logs"
DEFAULT_OUTPUT_FOLDER = "output"

DEFAULT_DELAY = 0

PARAMS = {
    "domain_only": False,
    "depth": DEFAULT_DEPTH,
    "domains": "https://animetake.tv",
    "silent": True,
    "log_file": '',
    "logs_folder": DEFAULT_LOG_FOLDER,
    "user_agent": None,
    "delay": DEFAULT_DELAY
}


def create_config(session, params=PARAMS):
    session.add(MuncherConfig(json_params=json.dumps(params)))
    session.commit()


def create_schedule(session, user_id, config_id):
    schedule = MuncherSchedule(user_id=user_id, config_id=config_id, start_datetime=datetime.datetime.now())
    session.add(schedule)
    session.commit()


if __name__ == '__main__':
    session = Session(engine)
    # create_config(session)
    create_schedule(session,2, 5)