from django.conf.urls import url
from views import update_columns

urlpatterns = [
    url(r'^update_columns', update_columns),
]
