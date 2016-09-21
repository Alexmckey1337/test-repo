# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import create_deal, create_partnership, update_deal, update_partnership, delete_deal, delete_partnership

urlpatterns = [
    url(r'^create_partnership', create_partnership),
    url(r'^update_partnership', update_partnership),
    url(r'^delete_partnership', delete_partnership),
    url(r'^create_deal', create_deal),
    url(r'^update_deal', update_deal),
    url(r'^delete_deal', delete_deal),

]
