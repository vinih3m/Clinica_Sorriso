def user_roles(request):
    if request.user.is_authenticated:
        return {
            'is_admin': request.user.groups.filter(name='Administrador').exists(),
            'is_dentista': request.user.groups.filter(name='Dentista').exists(),
            'is_recepcionista': request.user.groups.filter(name='Recepcionista').exists(),
        }

    return {
        'is_admin': False,
        'is_dentista': False,
        'is_recepcionista': False,
    }