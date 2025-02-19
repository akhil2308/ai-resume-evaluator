import os
from decouple import Csv, config

# Core Settings
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

ALLOWED_EXTENSIONS = ["pdf", "docx"]
MAX_FILES = 5

# Openai Config
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_MODEL = os.getenv('OPENAI_API_MODEL')

# Logging Configuration
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[{asctime}] [{process}] [{levelname}] {module}.{funcName}:{lineno} - {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S %z",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",  # Note: this handler will only emit INFO and higher messages.
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # The root logger; using an empty string "" applies it to all modules
        "": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
    },
}