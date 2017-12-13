from django.contrib.auth.decorators import login_required
from django.shortcuts import render


__all__ = ['privacy_policy', 'ticket_scanner', 'calls']


def privacy_policy(request):
    """For mobile clients"""
    ctx = {}
    return render(request, 'privacy_policy.html', context=ctx)


@login_required(login_url='entry')
def ticket_scanner(request):
    ctx = {}
    return render(request, 'ticket_scanner.html', context=ctx)


@login_required(login_url='entry')
def calls(request):
    ctx = {
        'types': ['in', 'out'],
        'dispositions': ['ANSWERED', 'OTHER'],
    }
    return render(request, 'calls.html', context=ctx)
