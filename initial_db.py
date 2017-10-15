from db import session, MuncherSchedule, MuncherConfig
import json

PARAMS = {
    "domain_only": False,
    "depth": 3,
    "domains": "https://animetake.tv",
    "silent": True,
    "log_file": '',
    "output_file": '',
    "logs_folder": 'logs',
    "output_folder": 'output',
}

if __name__ == '__main__':
    print(len(json.dumps(PARAMS)))
    config = MuncherConfig(json_params=json.dumps(PARAMS))
    session.add(config)
    session.commit()
    print(config.id)
    print('done')
