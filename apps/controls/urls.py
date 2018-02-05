from apps.controls import views
from django.urls import reverse, path
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def redirect_to_controls(request):
    if not request.user.is_staff:
        return redirect(reverse('db:people'))
    return redirect(reverse('controls:db_access_list'))

app_name = 'controls'

urlpatterns = [
    path('', login_required(redirect_to_controls, login_url='entry'), name='main'),
    path('db_access/', views.db_access_list, name='db_access_list'),
    path('db_access/<int:pk>/', views.db_access_detail, name='db_access_detail'),
    path('summit_panel/', views.summit_panel_list, name='summit_panel'),
]
