import time
from core.logger import KotizoLogger

logger = KotizoLogger('middleware')


class KotizoPerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        debut = time.time()
        response = self.get_response(request)
        duree = time.time() - debut

        if duree > 2.0:
            logger.warning('requete_lente', {
                'path': request.path,
                'method': request.method,
                'status': response.status_code,
            }, duree)

        return response
