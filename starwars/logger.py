import inspect
import json
import logging
import sys
import traceback
from datetime import datetime, date
import os
from logging.handlers import RotatingFileHandler

from decouple import config
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


def fetch_loging_function_name(f_p=3) -> str:
    try:
        frames = traceback.walk_stack(None)
        s = traceback.StackSummary.extract(frames)
        f = s[f_p]
        function_name = str(f.name)
    except Exception:
        function_name = ''
    return function_name


class Logger:

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
        file_name = config('APP_LOG_FILE')
        log_dir = config('LOG_DIR')
        file_path = os.path.join(log_dir, file_name + '.log')
        self._logger= logging.getLogger(file_name)

        if config('LOG_LEVEL') == "DEBUG":
            log_handler = logging.StreamHandler()
            log_handler.setLevel(logging.DEBUG)
        else:
            if not os.path.exists(log_dir):
                os.mkdir(log_dir)
            log_handler = RotatingFileHandler(
                file_path,
                maxBytes=10,
                backupCount=0
            )
            log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(formatter)
        self._logger.addHandler(log_handler)

    def error(self, msg):
        data_dict, func_name = self.generate_data_for_logger(level='ERROR', msg=msg)
        self._logger.error(data_dict)

    def info(self, msg):
        data_dict, func_name = self.generate_data_for_logger(level='INFO', msg=msg)
        self._logger.info(data_dict)

    def warn(self, msg):
        data_dict, func_name = self.generate_data_for_logger(level='WARN', msg=msg)
        self._logger.warning(data_dict)

    def debug(self, msg):
        data_dict, func_name = self.generate_data_for_logger(level='DEBUG', msg=msg)
        self._logger.debug(data_dict)

    def critical(self, msg):
        data_dict, func_name = self.generate_data_for_logger(level='CRITICAL', msg=msg)
        self._logger.critical(data_dict)

    def generate_data_for_logger(self, level, msg):
        function_name = fetch_loging_function_name()
        host_name = os.getenv('HOSTNAME')
        data_dict = {
            'host_name': host_name if host_name else 'default',
            'service': 'starwars',
            'log_level': level,
            'index': 'cr_' + str(datetime.today()),
            'message': '',
            'function_name': str(function_name)
        }
        if level == 'ERROR':
            data_dict.update({'traceback': traceback.format_exc()})
        if type(msg) == dict:
            data_dict.update(**msg)
        elif type(msg) == str:
            data_dict['message'] = msg
        else:
            data_dict['message'] = str(msg)
        try:
            return json.dumps(data_dict), str(function_name)
        except Exception:
            return json.dumps(data_dict, default=self.serialize_sets), str(function_name)

    @staticmethod
    def serialize_sets(obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, (datetime, date)):
            return str(obj)

        return obj

