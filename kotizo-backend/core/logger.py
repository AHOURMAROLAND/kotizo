import json
import logging
import time
from django.utils import timezone


class KotizoLogger:
    def __init__(self, module):
        self.module = module
        self.logger = logging.getLogger(module)

    def _log(self, level, action, data=None, duree=None):
        entry = {
            'timestamp': timezone.now().isoformat(),
            'module': self.module,
            'action': action,
            'data': data or {},
        }
        if duree is not None:
            entry['duree_ms'] = round(duree * 1000, 2)
        getattr(self.logger, level)(json.dumps(entry, ensure_ascii=False))

    def info(self, action, data=None, duree=None):
        self._log('info', action, data, duree)

    def error(self, action, data=None, duree=None):
        self._log('error', action, data, duree)

    def warning(self, action, data=None, duree=None):
        self._log('warning', action, data, duree)

    def debut(self):
        return time.time()

    def fin(self, debut):
        return time.time() - debut
