from enum import Enum


class PrescriptionRequiredEnum(Enum):
    YES = "Yes"
    NO = "No"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.capitalize()) for item in cls]




class UsersRoles(Enum):
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    GUEST = "Guest"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.capitalize()) for item in cls]