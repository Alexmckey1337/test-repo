from account.models import CustomUser

arr = []


def print_user_emails():
    for user in CustomUser.objects.all():
        if user.email and ('@' and '.') in user.email:
            arr.append(user.email)

    print(len(arr))
    with open('emails.txt', 'w') as file:
        for email in arr:
            file.write(email + '\n')

