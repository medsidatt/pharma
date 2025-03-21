def is_not_customer(user):
    return user.is_authenticated and not user.is_customer

def is_not_authenticated(user):
    return not user.is_authenticated
