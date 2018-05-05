from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse, path, include

from main import views


def redirect_to_churches(request):
    if not request.user.can_see_churches():
        return redirect(reverse('db:people'))
    return redirect(reverse('db:churches'))


def redirect_to_map_churches(request):
    return redirect(reverse('map:churches'))


database_patterns = (
    [
        path('', login_required(redirect_to_churches, login_url='entry'), name='main'),
        path('people/', views.PeopleListView.as_view(), name='people'),
        path('churches/', views.ChurchListView.as_view(), name='churches'),
        path('home_groups/', views.HomeGroupListView.as_view(), name='home_groups'),
    ], 'db')

map_patterns = (
    [
        path('', login_required(redirect_to_map_churches, login_url='entry'), name='main'),
        path('churches/', views.ChurchMapView.as_view(), name='churches'),
        path('home_groups/', views.HomeGroupMapView.as_view(), name='home_groups'),
    ], 'map')

urlpatterns = [
    path('', views.index, name='index'),
    path('entry/', views.entry, name='entry'),
    path('entry/restore/', views.restore, name='restore'),
    path('password_view/<str:activation_key>/', views.edit_pass, name='password_view'),

    path('account/', include('apps.account.urls', namespace='account')),
    path('db/', include(database_patterns, namespace='db')),
    path('map/', include(map_patterns, namespace='map')),
    path('events/', include('apps.event.urls', namespace='events')),
    path('partner/', include('apps.partnership.urls', namespace='partner')),
    path('payment/', include('apps.payment.urls', namespace='payment')),
    path('summits/', include('apps.summit.urls', namespace='summit')),
    path('tasks/', include('apps.task.urls', namespace='tasks')),

    path('churches/<int:pk>/', views.ChurchDetailView.as_view(), name='church_detail'),
    path('home_groups/<int:pk>/', views.HomeGroupDetailView.as_view(), name='home_group_detail'),

    path('sc/', views.search_city, name='search_city'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),  # for mobile app
    path('ticket_scanner/', views.ticket_scanner, name='ticket_scanner'),
    path('app/', views.app_download, name='app_download'),
    path('structure/', views.structure, name='structure-top'),
    path('structure/<int:pk>/', views.structure, name='structure-detail'),
    path('structure/<int:pk>/<str:name>.pdf', views.structure_to_pdf, name='structure_to_pdf-detail'),
    path('structure/top.pdf', views.structure_to_pdf, name='structure_to_pdf-top'),
    path('calls/', views.calls, name='calls'),
    path('controls/', include('apps.controls.urls', namespace='controls')),
    path('help/', include('apps.help.urls', namespace='help')),
    path('reference/', views.reference, name='reference'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
