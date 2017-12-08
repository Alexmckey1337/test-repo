def create_token(token_model, user, serializer):
    token = token_model.objects.create(user=user)
    return token
