from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from task import views

app_name = 'tasks'


def redirect_to_tasks(request):
    if not request.user.hierarchy.level <= 1:
        return redirect(reverse('db:people'))
    return redirect(reverse('tasks:task_list'))


urlpatterns = [
    url(r'^$', login_required(redirect_to_tasks, login_url='entry'), name='main'),
    url(r'^all/$', views.task_list, name='task_list'),
]
