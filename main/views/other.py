from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

from apps.account.models import CustomUser
from apps.summit.utils import NumberedCanvas

__all__ = ['privacy_policy', 'ticket_scanner', 'calls', 'structure', 'structure_to_pdf']


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


@login_required(login_url='entry')
def structure(request, pk=None):
    if not request.user.is_staff:
        raise PermissionDenied
    user = None
    # users = CustomUser.get_root_nodes().order_by('last_name', 'first_name', 'middle_name')
    users = CustomUser.get_root_nodes().order_by('-numchild', 'last_name', 'first_name', 'middle_name')
    if pk:
        user = get_object_or_404(CustomUser, pk=pk)
        # users = user.disciples.order_by('last_name', 'first_name', 'middle_name')
        users = user.disciples.order_by('-numchild', 'last_name', 'first_name', 'middle_name')
    ctx = {
        'user': user,
        'users': users,
    }
    return render(request, 'structure.html', context=ctx)


@login_required(login_url='entry')
def structure_to_pdf(request, pk=None):
    if not request.user.is_staff:
        raise PermissionDenied
    user = None
    users = CustomUser.get_root_nodes().order_by('last_name', 'first_name', 'middle_name')
    # users = CustomUser.get_root_nodes().order_by('-numchild', 'last_name', 'first_name', 'middle_name')
    if pk:
        user = get_object_or_404(CustomUser, pk=pk)
        users = user.disciples.order_by('last_name', 'first_name', 'middle_name')
        # users = user.disciples.order_by('-numchild', 'last_name', 'first_name', 'middle_name')

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
            ' > '.join(['TOP'] + [u.fullname for u in user.get_ancestors()] + [user.fullname]), styles['Header2']))
    else:
        elements.append(Paragraph(
            'TOP', styles['Header2']))
    table_data = list()
    for u in users:
        table_data.append([u.fullname, u.hierarchy or '', ', '.join(u.departments.values_list('title', flat=True))])
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
