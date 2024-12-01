from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom manager for handling user creation and modification.

    Methods:
        - create_user: Creates a new regular user.
        - create_superuser: Creates a new superuser with elevated permissions.
        - remove_user: Deactivates a user based on their email.
        - update_user: Updates user information by email.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular user with the given email, username,
        and password.
        """
        if not email:
            raise ValueError("The email field is required")

        if password is None:
            raise ValueError("The password field is required")


        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def deactivate_user(self, email):
        """
        Deactivate a user by setting their 'is_active' field to False.

        If no user is found, it raises a `User.DoesNotExist` exception.
        """
        try:
            user = self.get(email=email)
            user.is_active = False
            user.save(using=self._db, update_fields=["is_active"])
        except self.model.DoesNotExist:
            raise ValueError(f"User with email: {email} does not exist")

    def activate_user(self, email):
        """
        Activate a user by setting their 'is_active' field to True.

        If no user is found, it raises a `User.DoesNotExist` exception.
        """
        try:
            user = self.get(email=email)
            user.is_active = True
            user.save(using=self._db, update_fields=["is_active"])
        except self.model.DoesNotExist:
            raise ValueError(f"User with email: {email} does not exist.")

    def update_user(self, email, **update_fields):
        """
        Update a user's information based on their email.
        The `updated_fields` argument contains the fields to update.
        If the user is not found, it raises a `User.DoesNotExist` exception.
        """
        try:
            user = self.get(email=email)
            for field, value in update_fields.items():
                    setattr(user, field, value)
            user.save(using=self._db)
        except self.model.DoesNotExist:
            raise ValueError(f"User with email: {email} does not exist")




