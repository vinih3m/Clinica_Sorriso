def user_roles(request):
    user = request.user

    return {
        "is_admin": user.is_authenticated and (
            user.is_superuser or user.groups.filter(name="Administrador").exists()
        ),
        "is_medico": user.is_authenticated and user.groups.filter(name="Medico").exists(),
        "is_recepcionista": user.is_authenticated and user.groups.filter(name="Recepcionista").exists(),
    }