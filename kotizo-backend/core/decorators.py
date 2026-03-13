import time
import functools
from core.logger import logger


def log_action(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            request = args[0] if args else None
            user_id = None
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                user_id = request.user.id

            logger.info(f'Debut -> {action_name}', user_id=user_id, action=action_name)

            try:
                result = func(*args, **kwargs)
                duration_ms = round((time.time() - start) * 1000, 2)
                logger.info(f'Succes -> {action_name} ({duration_ms}ms)', user_id=user_id, action=action_name)
                return result
            except Exception as e:
                logger.error(f'Erreur -> {action_name} : {str(e)}', user_id=user_id, action=action_name)
                raise

        return wrapper
    return decorator