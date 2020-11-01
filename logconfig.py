import logging
import logging.config
from pathlib import Path

import yaml

log_format: str = '%(asctime)-15s %(user)-8s %(message)s'
log_defaults = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}


def applyLogDefaults():
    logging.basicConfig(format=log_format, level=logging.DEBUG)
    log_yaml_path = Path('config.yaml')

    logging.config.dictConfig(log_defaults)
    if log_yaml_path.exists():
        with open(log_yaml_path, 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
