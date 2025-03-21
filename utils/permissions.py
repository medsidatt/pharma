def is_not_customer(user):
    return user.is_authenticated and not user.is_customer

def is_customer(user):
    return user.is_authenticated and user.is_customer

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_not_authenticated(user):
    return not user.is_authenticated

