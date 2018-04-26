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


@app.task(name='users_is_stable_review', ignore_result=True,
          max_retries=3, default_retry_delay=600)
def users_is_stable_review():
    raw = """
           SELECT "account_customuser"."user_ptr_id",
           (SELECT array_agg(U0.attended)
           FROM "event_meetingattend" U0
           WHERE U0.id IN (SELECT U1.id
           FROM "event_meetingattend" U1
           WHERE U1."user_id" = ("account_customuser"."user_ptr_id")
           ORDER BY U1.id DESC LIMIT 4)
           GROUP BY U0."user_id") AS "attend"
           FROM "account_customuser";
           """

    qs = CustomUser.objects.raw(raw)
    meeting_visitors = [user for user in list(qs) if user.attend and len(user.attend) == 4]

    users_to_unstable = [user.id for user in meeting_visitors if user.is_stable and not any(user.attend)]
    CustomUser.objects.filter(id__in=users_to_unstable).update(is_stable=False)

    users_mark_stable = [user.id for user in meeting_visitors if not user.is_stable and all(user.attend)]
    CustomUser.objects.filter(id__in=users_mark_stable).update(is_stable=True)
