from account.models import CustomUser
from django.db.models import Q


def print_phone_numbers_ukraine():
    """
    Create a txt file with users phone numbers with required filters.
    Used by broadcast SMS mailing in Ukraine.
    """
    phone_numbers = []
    for user in CustomUser.objects.filter(phone_number__isnull=False).filter(is_active=True).filter(Q(
            phone_number__startswith='06') | Q(phone_number__startswith='07') | Q(
            phone_number__startswith='09') | Q(phone_number__startswith='+380') | Q(
            phone_number__startswith='380') | Q(phone_number__startswith='+09')):

        phone_number = ''.join([x for x in user.phone_number if x.isdigit()])
        if 11 <= len(phone_number) <= 13 and '9' * 6 not in phone_number and '0' * 6 not in phone_number:
            phone_numbers.append(phone_number)

    phone_numbers = list(set(phone_numbers))
    with open('phone_numbers_ukraine.txt', 'w') as file:
        for number in phone_numbers:
            file.write(number + '\n')

    return 'Finish, count: %s' % len(phone_numbers)


def print_phone_numbers_other():
    """
    Other World (without Ukraine)
    """
    phone_numbers = []
    for user in CustomUser.objects.filter(phone_number__isnull=False, is_active=True).exclude(Q(
        phone_number__startswith='06') | Q(phone_number__startswith='07') | Q(
        phone_number__startswith='09') | Q(phone_number__startswith='+380') | Q(
        phone_number__startswith='380') | Q(phone_number__startswith='+06') | Q(
        phone_number__startswith='+07') | Q(phone_number__startswith='044')):

        if '+' in user.phone_number:
            valid_number = user.phone_number.split('+')[1]
        else:
            valid_number = user.phone_number

        valid_number = ''.join([x for x in valid_number if x.isdigit()])
        if 11 <= len(valid_number) <= 13 and '9' * 6 not in valid_number and '0' * 6 not in valid_number:
            phone_numbers.append(valid_number)

    for number in phone_numbers:
        if number.startswith('380'):
            phone_numbers.remove(number)

    phone_numbers = list(set(phone_numbers))
    with open('phone_numbers_other.txt', 'w') as file:
        for number in phone_numbers:
            file.write(number + '\n')

    return 'Finish, count: %s' % len(phone_numbers)
