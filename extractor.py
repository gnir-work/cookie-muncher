from sqlalchemy.orm import Session

from db import engine, MuncherSchedule


class Extractor(object):
    def __init__(self, schedule_id):
        self.session = Session(engine)
        self.schedule = self.session.query(MuncherSchedule).get(schedule_id)