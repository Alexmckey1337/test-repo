from apps.zmail.defaults import SEND_RETRY_DELAY, SEND_MAX_TIME, SEND_RETRY

from apps.zmail.utils import Sender
from edem.settings.celery import app


@app.task(name='send_zmail', default_retry_delay=SEND_RETRY_DELAY)
def send_zmail(*args, **kwargs):

    retry_delay = kwargs.pop('retry_delay', SEND_RETRY_DELAY)
    time_limit = kwargs.pop('time_limit', SEND_MAX_TIME)
    max_retries = kwargs.pop('max_retries', SEND_RETRY)
    retry = kwargs.pop('retry', True)

    try:
        return Sender(*args, **kwargs).send()
    except Exception as exc:
        if retry is True and max_retries:
            raise send_zmail.retry(
                retry=retry, max_retries=max_retries,
                countdown=retry_delay, exc=exc,
                time_limit=time_limit,
            )
        raise
