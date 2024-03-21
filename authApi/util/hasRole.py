
def get_role(user):
    if user.is_superuser and user.is_staff:
        return "Administrador"
    elif user.is_staff:
        return "Encargado"
    return "Beca"