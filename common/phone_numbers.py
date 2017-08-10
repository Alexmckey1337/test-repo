from account.models import CustomUser


def print_phone_numbers():
    with open('phone_numbers.txt', 'w') as file:
        for user in CustomUser.objects.filter(phone_number__isnull=False):
            file.write(''.join([x for x in user.phone_number if x.isdigit()]) + '\n')

    return 'Finish'
