import pathlib
import os

import yaml
import trafaret as trf


PATH = pathlib.Path(__file__).parent.parent
settings_file = os.environ.get('SETTINGS_FILE', 'local.yaml')
DEFAULT_CONFIG_PATH = PATH / 'config' / settings_file

CONFIG_TRAFARET = trf.Dict({
    trf.Key('database'):
        trf.Dict({
            'host': trf.String(),
            'port': trf.Int(),
            'database': trf.String(),
            'user': trf.String(),
            'password': trf.String(),
        }),
    trf.Key('cache'):
        trf.Dict({
            'host': trf.String(),
            'port': trf.Int(),
        })
})

with open(DEFAULT_CONFIG_PATH, 'r') as stream:
    CONFIG = yaml.safe_load(stream)

CONFIG_TRAFARET.check(CONFIG)

_db_conf = CONFIG['database']
DATABASE_URL = (
    f'postgres://{_db_conf["user"]}:{_db_conf["password"]}@{_db_conf["host"]}'
    f':{_db_conf["port"]}/{_db_conf["database"]}'
)

SECRET_KEY = os.environ.get('SECRET_KEY', 'testkey')

DEFAULT_LOGIN_TTL = 180 * 24 * 60
