
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import inspect
import logging
import sys
from os.path import join
from logging.handlers import RotatingFileHandler


class LOG:
    """
    Custom logger class that acts like logging.Logger
    The logger name is automatically generated by the module of the caller

    Usage:
        >>> LOG.debug('My message: %s', debug_str)
        13:12:43.673 - :<module>:1 - DEBUG - My message: hi
        >>> LOG('custom_name').debug('Another message')
        13:13:10.462 - custom_name - DEBUG - Another message
    """
    base_path = "stdout"
    fmt = '%(asctime)s.%(msecs)03d - ' \
          '%(name)s - %(levelname)s - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    max_bytes = 50000000
    backup_count = 3
    name = 'OVOS'
    level = "DEBUG"
    _loggers = {}

    @classmethod
    def init(cls, config=None):
        config = config or {}
        cls.base_path = config.get("path", "stdout")
        cls.max_bytes = config.get("max_bytes", 50000000)
        cls.backup_count = config.get("backup_count", 3)
        cls.level = config.get("level", "DEBUG")

    @classmethod
    def create_logger(cls, name, tostdout=False):
        if name in cls._loggers:
            return cls._loggers[name]
        logger = logging.getLogger(name)
        logger.propagate = False
        # also log to stdout
        if tostdout:
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(cls.formatter)
            logger.addHandler(stdout_handler)
        # log to file
        if cls.base_path != "stdout":
            path = join(cls.base_path,
                        cls.name.lower().strip() + ".log")
            handler = RotatingFileHandler(path, maxBytes=cls.max_bytes,
                                          backupCount=cls.backup_count)
            handler.setFormatter(cls.formatter)
            logger.addHandler(handler)
        logger.setLevel(cls.level)
        cls._loggers[name] = logger
        return logger

    @classmethod
    def set_level(cls, level):
        cls.level = level
        for l in cls._loggers:
            cls._loggers[l].setLevel(level)

    @classmethod
    def _get_real_logger(cls):
        name = ""
        if cls.name is not None:
            name = cls.name + " - "

        # Stack:
        # [0] - _log()
        # [1] - debug(), info(), warning(), or error()
        # [2] - caller
        stack = inspect.stack()

        # Record:
        # [0] - frame object
        # [1] - filename
        # [2] - line number
        # [3] - function
        # ...
        record = stack[2]
        mod = inspect.getmodule(record[0])
        module_name = mod.__name__ if mod else ''
        name += module_name + ':' + record[3] + ':' + str(record[2])

        return cls.create_logger(name)

    @classmethod
    def info(cls, *args, **kwargs):
        cls._get_real_logger().info(*args, **kwargs)

    @classmethod
    def debug(cls, *args, **kwargs):
        cls._get_real_logger().debug(*args, **kwargs)

    @classmethod
    def warning(cls, *args, **kwargs):
        cls._get_real_logger().warning(*args, **kwargs)

    @classmethod
    def error(cls, *args, **kwargs):
        cls._get_real_logger().error(*args, **kwargs)

    @classmethod
    def exception(cls, *args, **kwargs):
        cls._get_real_logger().exception(*args, **kwargs)


