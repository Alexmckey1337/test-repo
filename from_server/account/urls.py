from django.conf.urls import url, include
import views
from views import *

urlpatterns = [
    url(r'^delete_user', delete_user),
    url(r'^login', login_view),
    url(r'^create_user', create_user),
    url(r'^send_password', send_password),
    url(r'^change_password', change_password),
    url(r'^logout', logout_view, name="logout"),

]
