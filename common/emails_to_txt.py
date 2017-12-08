from apps.account.models import CustomUser


def print_emails():
    email_list = []
    for user in CustomUser.objects.filter(is_active=True):
        if user.email and ('@' and '.') in user.email:
            email_list.append(user.email)

    with open('emails.txt', 'w') as file:
        for email in email_list:
            file.write(email + '\n')

    return 'Finish with %s emails' % len(email_list)
