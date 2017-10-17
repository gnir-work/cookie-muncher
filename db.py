from sqlalchemy.engine.url import URL
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine

DB_URL = URL(drivername='mysql+pymysql', username='nir', password='geller', host='localhost',
             port=3306, database='Marketing1')

Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine(DB_URL)

# # reflect the tables
Base.prepare(engine, reflect=True)
#
# # mapped classes are now created with names by default
# # matching that of the table name.
Cookies = Base.classes.tblCookies
CookieInfo = Base.classes.tblCookie_Info
ExtractedCookies = Base.classes.tblExtracted_Cookies
MuncherConfig = Base.classes.tblMuncher_Config
MuncherSchedule = Base.classes.tblMuncher_Schedule
MuncherStats = Base.classes.tbl_Muncher_Stats
UrlScans = Base.classes.tblUrl_Scans



