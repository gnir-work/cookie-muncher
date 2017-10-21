"""
A basic scrapper which receives a domain name and returns all of the links in the domain.
"""
import argparse
from datetime import datetime as dt, datetime

from sqlalchemy.orm import Session

from dotmap import DotMap
from sqlalchemy import exists

from cookieMuncher.spiders.cookie_muncher import crawl
import os
import json
from urllib.parse import urlparse
from db import engine, MuncherConfig, MuncherSchedule, MuncherStats
from utils import check_directory_exists, LOG_FIXTURE, create_parser


def generate_file_name(folder, schedule_id, fixture):
    """
    Creates the file name from the folder and domains that the crawler will crawl.
    the file name will be: [datetime] [net locations of domains given].[fixture]
    :param folder: The folder where the file we be saved
    :param domains: The domains the crawler will crawl.
    :param fixture: The fixture of the file.
    :return: The full path to the file.
    """
    return os.path.join(folder,
                        "urls_scan_schedule_{}_{}.{}".format(schedule_id, str(dt.now()).replace(':', '.'),
                                                             fixture))


def generate_netlocations_from_domains(domains):
    return list({urlparse(domain).netloc for domain in domains.split()})


def format_arguments(args, schedule_id):
    """
    Formats the arguments given to the script.
    :param args: The args given to the script.
    :return: The formatted args.
    """
    allowed_domains = []
    if args.domain_only:
        allowed_domains = generate_netlocations_from_domains(args.domains)
    if args.silent:
        args.log_file = None
    else:
        args.log_file = generate_file_name(args.logs_folder, schedule_id, LOG_FIXTURE)
    args.domains = args.domains.split()
    check_directory_exists(args.logs_folder)
    return args, allowed_domains


def create_muncher_stats(session, schedule_id):
    """
    Creates the stats table for this schedule, if a table already exists for this schedule aborts the run.
    :param Session session: The session with the mysql db.
    :param schedule_id: The schedule id for this run.
    :return: True if the stats was created successfully false otherwise.
    """
    if session.query(exists().where(MuncherStats.schedule_id == schedule_id)).scalar():
        print("There is already a muncher stats with the schedule id of {}".format(schedule_id))
        return None
    else:
        stats = MuncherStats(schedule_id=schedule_id)
        session.add(stats)
        session.commit()
        return stats


def run(parser):
    """
    Creates the crawler using the parser to parse the cli arguments.
    :param parser: A configured instance of argsParser
    :return: A configured crawler instance.
    """
    start = datetime.now()
    session = Session(engine)
    id = parser.parse_args().id
    schedule = session.query(MuncherSchedule).get(id)
    config = session.query(MuncherConfig).get(schedule.config_id)
    stats = create_muncher_stats(session, id)
    if stats:
        args, allowed_domains = format_arguments(DotMap(json.loads(config.json_params)), id)
        stats.urls_log_path = args.log_file
        session.commit()
        crawl(id, args.domains, allowed_domains, args.depth, args.silent, args.log_file, args.delay, args.user_agent)
        stats.url_scan_duration = (datetime.now() - start).seconds
        session.commit()
    session.close()


if __name__ == '__main__':
    parser = create_parser()
    run(parser)
