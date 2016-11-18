import os
from io import BytesIO

import requests
from PIL import Image
from django.conf import settings
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from summit.models import SummitAnket


def generate_ticket(code):
    if code != '00000000':
        anket = get_object_or_404(SummitAnket, code=code)
        user = anket.user
        first_name = user.first_name
        last_name = user.last_name
    else:
        first_name = 'No_name'
        last_name = 'No_name'

    logo = os.path.join(settings.MEDIA_ROOT, 'ticket.jpg')
    url = 'http://barcode.tec-it.com/barcode.ashx?translate-esc=off&data={code}&code=Code128&dpi=600&imagetype=Jpg&rotation=90&color=000000&bgcolor=FFFFFF&download=true'.format(
        code=code)

    r = requests.get(url)

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    w = .035 * A4[0] * cm
    v = .035 * A4[1] * cm - w * 941 / 2241

    try:
        c.drawImage(logo, 0, v, width=w, height=w * 941 / 2241)
    except OSError:
        pass
    c.setFont('FreeSans', 46 * w / 2241)
    c.drawString(80 * w / 2241, 165 * w / 2241 + v, first_name)
    c.drawString(970 * w / 2241, 165 * w / 2241 + v, last_name)
    c.drawImage(ImageReader(Image.open(BytesIO(r.content))), 1950 * w / 2241, 200 * w / 2241 + v, 645 / 2 * w / 2241,
                988 / 2 * w / 2241)
    # c.setStrokeColor(white)
    # c.setLineWidth(80)
    # c.line(2250, 20, 2250, 950)

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

# def send_ticket(summit_anket):
#     template_name = 'email/summit_ticket.html'
#     ctx = {}
#     main_email = settings.EMAIL_HOST_USER or ''
#     recipient_list = [summit_anket.user.email]
#
#     html_template = get_template(template_name)
#     subject = ctx.get('subject', 'Билет')
#     message = ctx.get('message', 'Билен на саммит {}'.format(summit_anket.summit))
#     from_email = 'Билет <{email}>'.format(email=main_email)
#     html_message = html_template.render(ctx)
#
#     mail = EmailMultiAlternatives(subject, message, from_email, recipient_list)
#     mail.attach_alternative(html_message, 'text/html')
#
#     mail.attach('{} ({}).pdf'.format(
#         summit_anket.user.fullname, summit_anket.code),
#         generate_ticket(summit_anket.code),
#         'application/pdf')
#
#     return mail.send()
