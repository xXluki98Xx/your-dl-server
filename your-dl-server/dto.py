import logging
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class dto():
    def __init__(self):
        self.string_bandwidth = '0'
        self.string_sublang = ''
        self.string_dublang = ''
        self.string_parameters = ''
        self.string_pathtoroot = ''
        self.string_cookiefile = ''
        self.string_logging = ''
        self.string_logPath = ''
        self.string_offset = ''
        
        self.int_retries = ''

        self.boolean_playlist = False
        self.boolean_removefiles = False
        self.boolean_verbose = False
        self.boolean_sync = False
        self.boolean_single = False
        self.boolean_axel = False
        self.boolean_space = False
        self.boolean_credential = False
        self.boolean_break = False
        self.boolean_skip_checks = False
        self.boolean_server = False
        self.boolean_downloader_legacy = False

        self.downloadList = []

        self.time_start = datetime.now()

        self.json_data = ''

        # Logging
        self.logger_formatter = logging.Formatter('%(asctime)s — %(levelname)s — %(message)s')
        self.logger_file = 'dl.log'
        self.logger = self.setInitLogger()


# getter and setter
# ----- # ----- # String
    def getBandwidth(self):
        return self.string_bandwidth
    def setBandwidth(self, swap):
        self.string_bandwidth = swap

    def getSubLang(self):
        return self.string_sublang
    def setSubLang(self, swap):
        self.string_sublang = swap

    def getDubLang(self):
        return self.string_dublang
    def setDubLang(self, swap):
        self.string_dublang = swap

    def getParameters(self):
        return self.string_parameters
    def setParameters(self, swap):
        self.string_parameters = swap

    def getPathToRoot(self):
        return self.string_pathtoroot
    def setPathToRoot(self, swap):
        self.string_pathtoroot = swap

    def getCookieFile(self):
        return self.string_cookiefile
    def setCookieFile(self, swap):
        self.string_cookiefile = swap

    def getLogger(self):
        return self.logger
    def setLogger(self, swap):
        self.string_logging = swap
        self.logger_level = getattr(logging, self.string_logging.upper(), logging.WARNING)

        if not isinstance(self.logger_level, int):
            raise ValueError('Invalid log level: %s' % self.logger_level)

        self.logger = self.get_logger()

    def setInitLogger(self):
        self.logger_level = getattr(logging, self.string_logging.upper(), logging.WARNING)

        if not isinstance(self.logger_level, int):
            raise ValueError('Invalid log level: %s' % self.logger_level)

        return self.get_logger()

    def getLogging(self):
        return self.string_logging
    def setLogging(self, swap):
        self.string_logging = swap

    def getLogPath(self):
        return self.string_logPath
    def setLogPath(self, swap):
        self.string_logPath = swap
        self.logger_file = self.string_logPath + '/dl.log'
        self.get_logger()

    def getOffset(self):
        return self.string_offset
    def setOffset(self, swap):
        self.string_offset = swap


# ----- # ----- # Int
    def getRetries(self):
        return self.int_retries
    def setRetries(self, swap):
        self.int_retries = swap


# ----- # ----- # Boolean
    def getPlaylist(self):
        return self.boolean_playlist
    def setPlaylist(self, swap):
        self.boolean_playlist = swap

    def getRemoveFiles(self):
        return self.boolean_removefiles
    def setRemoveFiles(self, swap):
        self.boolean_removefiles = swap

    def getVerbose(self):
        return self.boolean_verbose
    def setVerbose(self, swap):
        self.boolean_verbose = swap
        self.get_logger()

    def getSync(self):
        return self.boolean_sync
    def setSync(self, swap):
        self.boolean_sync = swap

    def getSingle(self):
        return self.boolean_single
    def setSingle(self, swap):
        self.boolean_single = swap

    def getAxel(self):
        return self.boolean_axel
    def setAxel(self, swap):
        self.boolean_axel = swap

    def getSpace(self):
        return self.boolean_space
    def setSpace(self, swap):
        self.boolean_space = swap

    def getCredentials(self):
        return self.boolean_credential
    def setCredentials(self, swap):
        self.boolean_credential = swap

    def getBreak(self):
        return self.boolean_break
    def setBreak(self, swap):
        self.boolean_break = swap

    def getSkipChecks(self):
        return self.boolean_skip_checks
    def setSkipChecks(self, swap):
        self.boolean_skip_checks = swap

    def getServer(self):
        return self.boolean_server
    def setServer(self, swap):
        self.boolean_server = swap

    def getDownloadLegacy(self):
        return self.boolean_downloader_legacy
    def setDownloadLegacy(self, swap):
        self.boolean_downloader_legacy = swap


# ----- # ----- # Time
    def getTimeStart(self):
        return self.time_start
    def setTimeStart(self, swap):
        self.time_start = swap


# ----- # ----- # Json
    def getData(self):
        return self.json_data
    def setData(self, swap):
        self.json_data = swap


# ----- # ----- # List
    def getDownloadList(self):
        return self.downloadList
    def setDownloadList(self, swap):
        self.downloadList = swap


# ----- # ----- # Logging
    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.logger_formatter)
        return console_handler

    def get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self.logger_file, when='midnight')
        file_handler.setFormatter(self.logger_formatter)
        return file_handler

    def get_logger(self):
        logger = logging.getLogger(__name__)

        if not logger.handlers:
            logger.setLevel(self.logger_level) # better to have too much log than not enough
            logger.addHandler(self.get_file_handler())

            if self.getVerbose():
                logger.addHandler(self.get_console_handler())

        else:
            for h in logger.handlers:
                logger.removeHandler(h)

            logger.setLevel(self.logger_level) # better to have too much log than not enough
            logger.addHandler(self.get_file_handler())

            if self.getVerbose():
                logger.addHandler(self.get_console_handler())

        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False
        return logger

    def publishLoggerInfo(self, message):
        self.logger.info(message)

    def publishLoggerDebug(self, message):
        self.logger.debug(message)

    def publishLoggerWarn(self, message):
        self.logger.warning(message)

    def publishLoggerError(self, message):
        self.logger.error(message)

    def publishLoggerCritical(self, message):
        self.logger.critical(message)
