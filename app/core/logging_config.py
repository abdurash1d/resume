import logging
import logging.config
import os
from pathlib import Path
from datetime import datetime

def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'standard',
                'filename': f'logs/error_{datetime.now().strftime("%Y%m%d")}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': True
            },
            'uvicorn': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            },
            'uvicorn.error': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'sqlalchemy': {
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(log_config)
