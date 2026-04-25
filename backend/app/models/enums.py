from enum import Enum


class UserRole(str, Enum):
    """System roles reserved for upcoming authentication and authorization modules."""

    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    TECH = "TECH"
    CLIENT = "CLIENT"
    DEALER = "DEALER"
