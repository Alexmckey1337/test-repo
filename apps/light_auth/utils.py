from collections.__init__ import OrderedDict
from urllib.parse import urlsplit

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from twilio.rest import Client

from apps.light_auth import app_settings


account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


def send_sms(template, phone, ctx):
    body = render_to_string(template, ctx)

    message = client.messages.create(
        body=body,
        from_=settings.TWILIO_FROM,
        to=phone
    )
    print(message.sid)
    print(phone, body, sep='\n\n', end='\n\n')


def build_absolute_uri(request, location, protocol=None):
    if request is None:
        site = Site.objects.get_current()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = '{proto}://{domain}{url}'.format(
                proto='http',
                domain=site.domain,
                url=location)
        else:
            uri = location
    else:
        uri = request.build_absolute_uri(location)
    if protocol:
        uri = protocol + ':' + uri.partition(':')[2]
    return uri


def get_phone_confirmation_url(request, phone_confirmation):
    # url = reverse("light_auth_confirm_phone", args=[phone_confirmation.key])
    url = 'https://vochurch.online/confirm_url/'
    ret = build_absolute_uri(request, url)
    return ret


def send_confirmation_sms(request, phone_confirmation, reset_password):
    # current_site = get_current_site(request)
    # activate_url = get_phone_confirmation_url(request, phone_confirmation)
    ctx = {
        "user": phone_confirmation.phone_number.auth_user,
        "phone": phone_confirmation.phone_number,
        # "activate_url": activate_url,
        # "current_site": current_site,
        "key": phone_confirmation.key,
    }
    if reset_password:
        sms_template = 'light_auth/sms/sms_confirmation_reset_password.txt'
    else:
        sms_template = 'light_auth/sms/sms_confirmation.txt'
    send_sms(sms_template, phone_confirmation.phone_number.phone, ctx)


def get_light_auth_user_model():
    try:
        return django_apps.get_model(app_settings.USER_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("LIGHT_AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "LIGHT_AUTH_USER_MODEL refers to model '%s' that has not been installed" % app_settings.USER_MODEL
        )


def make_phone_number(phone_number):
    phone_number = '+' + ''.join([x for x in phone_number if x.isdigit()])
    if len(phone_number) < 11:
        return None
    return phone_number


def cleanup_phone_numbers(phone_numbers):
    from apps.light_auth.models import PhoneNumber
    p2n = OrderedDict()  # maps phone to PhoneNumber
    primary_phones = []
    verified_phones = []
    primary_verified_phones = []
    for phone_number in phone_numbers:
        # Pick up only valid ones...
        phone = make_phone_number(phone_number.phone)
        if not phone:
            continue
        # ... and non-conflicting ones...
        if (PhoneNumber.objects.filter(phone__iexact=phone).exists()):
            continue
        n = p2n.get(phone.lower())
        if n:
            n.primary = n.primary or phone_number.primary
            n.verified = n.verified or phone_number.verified
        else:
            n = phone_number
            p2n[phone.lower()] = n
        if n.primary:
            primary_phones.append(n)
            if n.verified:
                primary_verified_phones.append(n)
        if n.verified:
            verified_phones.append(n)
    # Now that we got things sorted out, let's assign a primary
    if primary_verified_phones:
        primary_phone = primary_verified_phones[0]
    elif verified_phones:
        # Pick any verified as primary
        primary_phone = verified_phones[0]
    elif primary_phones:
        # Okay, let's pick primary then, even if unverified
        primary_phone = primary_phones[0]
    elif p2n:
        # Pick the first
        primary_phone = list(p2n.keys())[0]
    else:
        # Empty
        primary_phone = None
    # There can only be one primary
    for n in p2n.values():
        n.primary = primary_phone.phone.lower() == n.phone.lower()
    return list(p2n.values()), primary_phone


def setup_user_phone(auth_user, phones):
    from apps.light_auth.models import PhoneNumber

    assert not PhoneNumber.objects.filter(auth_user=auth_user).exists()
    phone_number = auth_user.user.phone_number
    priority_phones = [PhoneNumber(auth_user=auth_user, phone=phone_number, primary=True, verified=False)]
    phones, primary = cleanup_phone_numbers(priority_phones + phones)
    for p in phones:
        p.user = auth_user
        p.save()
    return primary
