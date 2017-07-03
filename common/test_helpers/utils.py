def get_real_user(request):
    """
    Returns `real_user`/`user` if user is authenticated else returns `None`

    :param request:
    :return: request.real_user or None
    """
    user = getattr(request, 'real_user', getattr(request, 'user', None))
    return user if user and user.is_authenticated else None
