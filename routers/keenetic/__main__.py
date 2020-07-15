import time
from .status.collector import StatusCollector
from .status.logger import log, error

COLLECT_THRESHOLD = 20  # seconds

log("Starting automation service loop")
last_collect = int(time.time())
while True:
    try:
        current_time = int(time.time())
        if current_time >= last_collect + COLLECT_THRESHOLD:
            last_collect = current_time
            StatusCollector("store")
        time.sleep(0.5)
    except Exception as e:
        error(e)
    except KeyboardInterrupt:
        log('Loop finished by user\'s request')
        break
