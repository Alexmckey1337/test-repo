import logging

from apps.account.models import CustomUser
from apps.hierarchy.models import Hierarchy
from edem.settings.celery import app


logger = logging.getLogger('tasks')


@app.task(name='improve_convert_to_congregation', ignore_result=True)
def improve_convert_to_congregation():
    congregation = Hierarchy.objects.get(code='congregation')
    converts = CustomUser.objects.filter(
        hierarchy__code='convert').extra(where=["age(repentance_date) >= interval '6 month'"])
    count = converts.update(hierarchy=congregation)
    if count > 0:
        logger.info(f'Improve from convert to congregation {count:0>6} people')
