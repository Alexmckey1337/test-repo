from django.conf.urls import url, include
from views import *

urlpatterns = [
    url(r'^update_last_call', update_last_call),
    #url(r'^login', login_view),
    #url(r'^create_user', create_user),
    #url(r'^change_password', change_password),
]