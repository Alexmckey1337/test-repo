from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.account.models import CustomUser
from apps.status.models import Division
from apps.task.models import TaskType


@login_required(login_url='entry')
def task_list(request):
    if not request.user.is_staff and not request.user.hierarchy:
        return redirect('/')

    ctx = {
        'divisions': Division.objects.all(),
        'executors': CustomUser.objects.for_user(request.user),
        'targets': CustomUser.objects.all(),
        'types': TaskType.objects.all(),
        'deal_status_options': [
            {'id': '0', 'title': 'Hе оплачена'},
            {'id': '1', 'title': 'Оплачена частично'},
            {'id': '2', 'title': 'Оплачена полностью'},
        ],
    }

    return render(request, 'tasks/task_list.html', context=ctx)
