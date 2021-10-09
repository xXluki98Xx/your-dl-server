import os
import sys
from datetime import datetime
from time import sleep

import ioutils


def watcher(dto, command, minutes, hours):
    interval = (float(minutes) + float(hours)*60)
    parameters = ioutils.getMainParametersFromDto(dto)

    try:
        startTime = datetime.now()
        
        while True:
            if ( (datetime.now() - startTime).seconds % (int(interval)*60) ) == 0:
                sleep(60)
                dto.publishLoggerInfo('watcher started with:\ndl.py {} --single {}'.format(parameters, command))
                os.system('dl.py {} -s {}'.format(parameters, command))

    except KeyboardInterrupt:
        os._exit(1)
    except:
        dto.publishLoggerError('watcher - error at: ' + command)
        dto.publishLoggerError('watcher - error: ' + str(sys.exc_info()))
