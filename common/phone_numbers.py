from account.models import CustomUser
from django.db.models import Q


def print_phone_numbers():
    """
    Create a txt file with users phone numbers with required filters.
    Used by broadcast SMS mailing.
    """
    phone_numbers = []
    for user in CustomUser.objects.filter(
            phone_number__isnull=False).filter(is_active=True).filter(Q(phone_number__startswith='06') | Q(
            phone_number__startswith='07') | Q(phone_number__startswith='09') | Q(phone_number__startswith='+380')):
        phone_number = ''.join([x for x in user.phone_number if x.isdigit()])
        if 11 <= len(phone_number) <= 13 and '9' * 6 not in phone_number and '0' * 6 not in phone_number:
            phone_numbers.append(phone_number)

    phone_numbers = list(set(phone_numbers))
    with open('phone_numbers.txt', 'w') as file:
        for number in phone_numbers:
            file.write(number + '\n')

    return 'Finish, count: %s' % len(phone_numbers)
