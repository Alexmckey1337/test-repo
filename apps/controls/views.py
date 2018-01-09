from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required(login_url='entry')
def db_access(request):
    if not request.user.is_staff:
        return redirect('/')

    ctx = {}

    return render(request, 'controls/db_access.html')
