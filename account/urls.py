from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^delete_user', delete_user),
    url(r'^login', login_view),
    url(r'^create_user', create_user),
    url(r'^send_password', send_password),
    url(r'^change_password', change_password),
    url(r'^logout', logout_view, name="logout"),
    url(r'^download_image', download_image),
    url(r'^password_forgot', password_forgot, ),
    url(r'^password_view/$', password_view, ),
    url(r'^password_view/(?P<activation_key>\w+)/$', password_view),
]
