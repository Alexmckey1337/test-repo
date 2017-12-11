from apps.group.models import HomeGroup, Church


def create_titles():
    models = [Church.objects.filter(title=''), HomeGroup.objects.filter(title='')]
    for model in models:
        for obj in model:
            obj.title = obj.get_title
            obj.save()
