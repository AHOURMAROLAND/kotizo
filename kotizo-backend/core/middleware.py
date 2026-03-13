import time
from core.logger import logger


class KotizoRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id

        logger.performance(
            f'{request.method} {request.path} -> {response.status_code}',
            duration_ms=duration_ms,
            endpoint=request.path,
            user_id=user_id,
        )

        if duration_ms > 2000:
            logger.warning(
                f'Requete lente : {request.path} ({duration_ms}ms)',
                user_id=user_id,
                duration_ms=duration_ms,
            )

        return response