import re

from django.db import models
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.contrib.auth.password_validation import (
    CommonPasswordValidator,
    UserAttributeSimilarityValidator
)
from django.utils.translation import gettext_lazy as _


class UserModelValidator:
    """
    A class containing static methods to validate various user-related
    attributes, including username, password, user station, and roles.
    """

    @staticmethod
    def username_validator(username, min_length=4, max_length=128):
        """
        Validates a username based on length and character constraints.

        Args:
            username (str): The username to validate.
            min_length (int): Minimum allowed length for the username.
            max_length (int): Maximum allowed length for the username.

        Raises:
            ValidationError: If the username does not meet the constraints.
        """
        if len(username) < min_length:
            raise ValidationError(
                _(
                    f"Username must be at least {min_length} characters long"
                )
            )
        if len(username) > max_length:
            raise ValidationError(
                _(
                    f"Username cannot be longer than {max_length} characters"
                )
            )

        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError(
                _(
                    "Username can only contain letters, numbers, underscores, and hyphens"
                )
            )

    @staticmethod
    def password_validator(password, user, min_length=8, special_char=False):
        """
        Validates a password based on length, complexity, and user similarity.

        Args:
            password (str): The password to validate.
            user (object): The user object to check for similarity.
            min_length (int): Minimum allowed length for the password.
            special_char (bool): Whether the password must include a special character.

        Raises:
            ValidationError: If the password does not meet the constraints.
        """

        UserAttributeSimilarityValidator().validate(password, user=user)

        if len(password) < min_length:
            raise ValidationError(
                _(
                    f"Password must be at least {min_length} characters long"
                )
            )

        complexity_checks = [
            (r'[A-Z]', "Password must contain at least one uppercase letter"),
            (r'[a-z]', "Password must contain at least one lowercase letter"),
            (r'[0-9]', "Password must contain at least one number"),
        ]

        if special_char:
            complexity_checks.append(
                (r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', "Password must contain at least one special character")
            )

        for pattern, error_message in complexity_checks:
            if not re.search(pattern, password):
                raise ValidationError(_(error_message))

        CommonPasswordValidator().validate(password, user=user)

    @staticmethod
    def user_station_validator(user_station, allowed_stations=("WH", "SP")):
        """
        Validates that the user's station is in the list of allowed stations.

        Args:
            user_station (str): The user's station identifier.
            allowed_stations (tuple): Tuple of allowed station identifiers.

        Raises:
            ValidationError: If the station is not allowed.
        """
        if user_station not in allowed_stations:
            raise ValidationError(
                _("User station must be one of the following: %(values)s"),
                params={"values": ", ".join(allowed_stations)}
            )

    @staticmethod
    def role_validator(role):
        """
        Validates a user's role field based on the associated User model.

        Args:
            role (object): The role object to validate.

        Raises:
            ValidationError: If the role does not meet the expected constraints.
        """

        from .models import User
        try:
            role_field = User._meta.get_field("role")
        except FieldDoesNotExist as e:
            raise ValidationError(
                _("Role field is not defined on the User model.")
            ) from e

        if role is None and not role_field.null:
            raise ValidationError(
                _("Role is required for this user"),
                code="role_required"
            )

        role_model = role_field.related_model
        if role and not isinstance(role, role_model):
            raise ValidationError(
                _("Invalid role type. Expected %(expected)s, got %(actual)s"),
                params={
                    "expected": role_model.__name__,
                    "actual": type(role).__name__
                },
                code="invalid_role_type"
            )

        if role is not None:
            if role_field.remote_field.on_delete == models.SET_NULL and role is None:
                return

            if not hasattr(role, "name") or not role.name:
                raise ValidationError(
                    _("Role must have a valid name"),
                    code="role_name_required"
                )


class OrgModelValidator:
    """
    A class containing static methods to validate organisation-related attributes.
    """

    @staticmethod
    def name_validator(name, max_length=125):
        """
        Validates an organisation name based on length and allowed characters.

        Args:
            name (str): The name of the organisation.
            max_length (int): Maximum allowed length for the name.

        Raises:
            ValidationError: If the name exceeds the length or contains invalid characters.
        """
        if len(name) > max_length:
            raise ValidationError(
                _("Organisation name cannot exceed %(max_length)d characters.") % {"max_length": max_length}
            )

        if not re.match(r'^[a-zA-Z0-9\s]+$', name):
            raise ValidationError(
                _("Organisation name can only contain letters, numbers and spaces.")
            )

    @staticmethod
    def owner_validator(owner):
        """
        Validates the owner attribute of an organisation.

        Args:
            owner (object): The owner to be validated.

        Raises:
            ValidationError:
                - If the owner field is not defined in the Organisation model.
                - If the owner is not an instance of the related User model.
        """
        from .models import Organisation

        try:
            owner_field = Organisation._meta.get_field("owner")
        except FieldDoesNotExist as e:
            raise ValidationError(
                _("owner field is not defined on the Organisation model")
            ) from e

        user_model = owner_field.related_model

        if not isinstance(owner, user_model):
            try:
                owner = user_model.objects.get(id=owner)
            except user_model.DoesNotExist as e:
                raise ValidationError(
                    _("User with the given ID does not exist")
                ) from e

        if not isinstance(owner, user_model):
            raise ValidationError(
                _("Invalid Organisation owner type. Expected %(expected)s, got %(actual)s"),
                params={
                    "expected": user_model.__name__,
                    "actual": type(owner).__name__
                },
                code="invalid_owner_type"
            )


class RoleModelValidator:
    """
    A class containing static methods to validate role-related attributes.
    """

    @staticmethod
    def name_validator(name):
        """
        Validates a role name against a predefined list of allowed roles.

        Args:
            name (str): The name of the role to validate.

        Raises:
            ValidationError: If the role name is not in the list of allowed roles.

        Allowed Roles:
            - "superadmin"
            - "admin"
            - "inventory manager"
            - "sales rep"
            - "invoice clerk"
        """
        if not isinstance(name, str):
            raise TypeError("Role name must be a string")
        

        allowed_roles = (
            "superadmin",
            "admin",
            "inventory manager",
            "sales rep",
            "invoice clerk"
        )
            
        if name.lower() not in allowed_roles:
            raise ValidationError(
                _("Invalid Role. Allowed Roles: %(roles)s"),
                params={"roles": ", ".join(allowed_roles)}
            )


class UserProfileValidator:
    """
    A utility class to validate a user instance for the UserProfile model.

    This class provides methods to validate that a user instance can be
    associated with a UserProfile. It performs checks to ensure the provided
    user is of the correct type and is active, raising validation errors if
    the conditions are not met.
    """

    @staticmethod
    def user_validator(user):
        """
        Validates a user instance for compatibility with the UserProfile model.

        Args:
            user (object): The user instance to validate.

        Raises:
            ValidationError: If any of the following conditions are met:
                - The `user` field is not defined on the `UserProfile` model.
                - The provided `user` is not an instance of the expected model.
                - The provided `user` is inactive.
        """
        from .models import UserProfile

        try:
            user_field = UserProfile._meta.get_field("user")
        except FieldDoesNotExist as e:
            raise ValidationError(
                _("user field is not defined on the UserProfile model")
            ) from e

        user_model = user_field.related_model

        if user and not isinstance(user, user_model):
            raise ValidationError(
                _("Invalid Profile User type. Expected %(expected)s, got %(actual)s"),
                params={
                    "expected": user_model.__name__,
                    "actual": type(user).__name__
                },
                code="invalid_profile_user_type"
            )

        if user and hasattr(user, "is_active") and not user.is_active:
            raise ValidationError(
                _("The user is inactive and cannot be assigned to a profile."),
                code="inactive_user"
            )
