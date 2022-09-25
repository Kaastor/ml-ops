import os

import elasticapm


_APM_SERVICE_NAME = 'apm-service-name'
_APM_URI = 'http://monitoring:8200'


def get_config():
    return {
        'SERVICE_NAME': _APM_SERVICE_NAME,
        'SERVER_URL': _APM_URI,
        'ENVIRONMENT': os.environ['ENV'],
        'SERVICE_VERSION': os.environ['VERSION']
    }


@elasticapm.capture_span()
def set_transaction_result():
    elasticapm.set_transaction_result("result")
