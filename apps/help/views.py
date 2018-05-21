from django.shortcuts import render
from apps.help.models import Manual, ManualCategory
from rest_framework.generics import get_object_or_404


def manual_category_list(request):
    ctx = {
        'categories': ManualCategory.objects.all(),
    }
    return render(request, 'help/category_list.html', ctx)


def manual_detail(request, pk):
    ctx = {
        'manual': Manual.objects.get(pk=pk)
    }
    return render(request, 'help/manual_detail.html', ctx)


