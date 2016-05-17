from django.conf.urls import url, include
from views import *

urlpatterns = [
    url(r'^create_event', create_event),
    url(r'^delete_event', delete_event),
    url(r'^create_participations', create_participations),
    url(r'^update_participation', update_participation),


    #url(r'^login', login_view),
    #url(r'^create_user', create_user),
    #url(r'^change_password', change_password),
]
