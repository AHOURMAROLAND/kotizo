import logging
import json
import traceback
from datetime import datetime


class KotizoJsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'app': 'kotizo',
            'level': record.levelname,
            'module': record.name,
            'message': record.getMessage(),
            'file': record.filename,
            'line': record.lineno,
        }
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if record.exc_info:
            log_data['traceback'] = traceback.format_exception(*record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


class KotizoLogger:
    def __init__(self, name='kotizo'):
        self.logger = logging.getLogger(name)

    def debug(self, message, **kwargs):
        self._log('debug', message, **kwargs)

    def info(self, message, **kwargs):
        self._log('info', message, **kwargs)

    def warning(self, message, **kwargs):
        self._log('warning', message, **kwargs)

    def error(self, message, **kwargs):
        self._log('error', message, **kwargs)

    def critical(self, message, **kwargs):
        self._log('critical', message, **kwargs)

    def paiement(self, message, user_id=None, montant=None, statut=None, **kwargs):
        self._log('info', f'[PAIEMENT] {message}', user_id=user_id, montant=montant, statut=statut, action='paiement', **kwargs)

    def cotisation(self, message, user_id=None, cotisation_id=None, **kwargs):
        self._log('info', f'[COTISATION] {message}', user_id=user_id, cotisation_id=cotisation_id, action='cotisation', **kwargs)

    def fraude(self, message, user_id=None, **kwargs):
        self._log('warning', f'[FRAUDE] {message}', user_id=user_id, action='fraude', **kwargs)

    def webhook(self, message, source=None, statut=None, **kwargs):
        self._log('info', f'[WEBHOOK] {message}', source=source, statut=statut, action='webhook', **kwargs)

    def performance(self, message, duration_ms=None, endpoint=None, **kwargs):
        level = 'warning' if duration_ms and duration_ms > 1000 else 'debug'
        self._log(level, f'[PERF] {message}', duration_ms=duration_ms, endpoint=endpoint, action='performance', **kwargs)

    def ia(self, message, user_id=None, action_ia=None, **kwargs):
        self._log('info', f'[IA] {message}', user_id=user_id, action=f'ia_{action_ia}', **kwargs)

    def auth(self, message, user_id=None, ip=None, **kwargs):
        self._log('info', f'[AUTH] {message}', user_id=user_id, ip=ip, action='auth', **kwargs)

    def _log(self, level, message, **kwargs):
        extra = {k: v for k, v in kwargs.items() if v is not None}
        getattr(self.logger, level)(message, extra=extra, exc_info=(level in ['error', 'critical']))


logger = KotizoLogger('kotizo')