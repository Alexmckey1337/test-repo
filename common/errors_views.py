from django.contrib.auth.decorators import login_required
from django.views.defaults import page_not_found, permission_denied, bad_request

page_not_found = login_required(page_not_found, login_url='entry')
permission_denied = login_required(permission_denied, login_url='entry')
bad_request = login_required(bad_request, login_url='entry')
