from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from reportlab.lib import colors
from reportlab.lib.colors import blue
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

from apps.account.models import CustomUser
from apps.summit.utils import NumberedCanvas

__all__ = ['privacy_policy', 'ticket_scanner', 'calls', 'structure', 'structure_to_pdf', 'app_download',
           'search_city']


def search_city(request):
    ctx = {}
    return render(request, 'search_city.html', context=ctx)


def privacy_policy(request):
    """For mobile clients"""
    ctx = {}
    return render(request, 'privacy_policy.html', context=ctx)


@login_required(login_url='entry')
def ticket_scanner(request):
    ctx = {}
    return render(request, 'ticket_scanner.html', context=ctx)


def app_download(request):
    """Page for mobile app download"""
    ctx = {}
    return render(request, 'app.html', context=ctx)


@login_required(login_url='entry')
def calls(request):
    ctx = {
        'types': [
            {'in': 'Входящие'},
            {'out': 'Исходящие'}
        ],
        'dispositions': [
            {'ANSWERED': 'Отвеченные'},
            {'OTHER': 'Остальные'}
        ]
    }
    return render(request, 'phone/index.html', context=ctx)


@login_required(login_url='entry')
def structure(request, pk=None):
    if not request.user.is_staff:
        raise PermissionDenied
    only_active = request.GET.get('only_active', None) is not None
    user = None
    # users = CustomUser.get_root_nodes().order_by('last_name', 'first_name', 'middle_name')
    users = CustomUser.get_root_nodes().order_by('-numchild', 'last_name', 'first_name', 'middle_name')
    if pk:
        user = get_object_or_404(CustomUser, pk=pk)
        # users = user.disciples.order_by('last_name', 'first_name', 'middle_name')
        users = user.disciples.order_by('-numchild', 'last_name', 'first_name', 'middle_name')
    ctx = {
        'only_active': only_active,
        'user': user,
        'users': users.filter(is_active=True) if only_active else users,
    }
    return render(request, 'structure.html', context=ctx)


@login_required(login_url='entry')
def structure_to_pdf(request, pk=None, name=''):
    if not request.user.is_staff:
        raise PermissionDenied
    only_active = request.GET.get('only_active', None) is not None
    user = None
    # users = CustomUser.get_root_nodes().order_by('last_name', 'first_name', 'middle_name')
    users = CustomUser.get_root_nodes().order_by('-numchild', 'last_name', 'first_name', 'middle_name')
    if pk:
        user = get_object_or_404(CustomUser, pk=pk)
        # users = user.disciples.order_by('last_name', 'first_name', 'middle_name')
        users = user.disciples.order_by('-numchild', 'last_name', 'first_name', 'middle_name')
    users = users.filter(is_active=True) if only_active else users

    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RightAlign', fontName='FreeSans', alignment=TA_RIGHT, fontSize=8))
    styles.add(ParagraphStyle(name='LeftAlign', fontName='FreeSans', alignment=TA_LEFT, fontSize=8))
    styles.add(ParagraphStyle(name='date', fontName='FreeSans', alignment=TA_RIGHT, fontSize=12))
    styles.add(ParagraphStyle(
        name='Header1', fontName='FreeSansBold', alignment=TA_LEFT, fontSize=16, spaceAfter=5))
    styles.add(ParagraphStyle(
        name='Header12', fontName='FreeSansBold', alignment=TA_LEFT, fontSize=14, spaceAfter=5))
    styles.add(ParagraphStyle(
        name='Header2', fontName='FreeSans', alignment=TA_LEFT, fontSize=12, spaceAfter=5))
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, rightMargin=72, leftMargin=72, topMargin=22, bottomMargin=22, pagesize=A4)
    elements = list()
    if user:
        elements.append(Paragraph(
            ' > '.join(
                ['<link href="{scheme}://{host}{pdf}" color="blue">TOP</link>'.format(
                    url=reverse('structure-top'),
                    pdf=reverse('structure_to_pdf-top'),
                    host=request.META.get('HTTP_HOST'),
                    scheme=request.is_secure() and 'https' or 'http'
                )] +
                [
                    '<link href="{scheme}://{host}{pdf}" color="blue">{name}</link>'.format(
                        name=u.fullname,
                        url=reverse('structure-detail', kwargs={'pk': u.pk}),
                        pdf=reverse('structure_to_pdf-detail', kwargs={'pk': u.pk, 'name': u.fullname}),
                        host=request.META.get('HTTP_HOST'),
                        scheme=request.is_secure() and 'https' or 'http'
                    )
                    for u in user.get_ancestors()] +
                [user.fullname]), styles['Header2']))
    else:
        elements.append(Paragraph('TOP', styles['Header2']))
    table_data = list()

    for u in users:
        username = u.fullname if u.is_leaf() else Paragraph(
            '{name} '
            '<link href="{scheme}://{host}{url}" color="blue">page</color></link> '
            '<link href="{scheme}://{host}{pdf}" color="red">pdf</link>'.format(
                name=u.fullname,
                url=reverse('structure-detail', kwargs={'pk': u.pk}),
                pdf=reverse('structure_to_pdf-detail', kwargs={'pk': u.pk, 'name': u.fullname}),
                host=request.META.get('HTTP_HOST'),
                scheme=request.is_secure() and 'https' or 'http'
            ), styles['LeftAlign'])
        table_data.append([
            username,
            u.hierarchy or '',
            ', '.join(u.departments.values_list('title', flat=True))
        ])
    table_data = [['ФИО', 'Иерархия', 'Департаменты']] + table_data
    user_table = Table(table_data, colWidths=[
        doc.width * 0.4, doc.width * 0.2, doc.width * 0.4], normalizedData=1)
    user_table.setStyle(TableStyle(
        [
            ('INNERGRID', (0, 0), (-1, -1), 0.15, colors.black),
            ('FONT', (0, 0), (-1, -1), 'FreeSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.15, colors.black),

            # ('FONTSIZE', (0, 0), (0, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),

            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'FreeSansBold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
    elements.append(user_table)
    doc.build(elements, canvasmaker=NumberedCanvas)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;'

    response.write(pdf)
    return response
