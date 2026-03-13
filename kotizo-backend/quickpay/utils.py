import random
import string
from .models import QuickPay


def generer_code_quickpay():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not QuickPay.objects.filter(code=code).exists():
            return code