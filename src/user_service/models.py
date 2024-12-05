from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom manager for handling user creation and modification.

    Methods:
        - create_user: Creates a new regular user.
        - create_superuser: Creates a new superuser with elevated permissions.
        - deactivate_user: Deactivates a user based on their email.
        - activate_user: Activates a user based on their email
        - update_user: Updates user information by email.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user with the given email, username, and
        password."""
        if not email:
            raise ValidationError(
                _("The email field is required"), code="email_required"
            )

        if password is None:
            raise ValidationError(
                _("The password field is required"), code="password_required"
            )

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user = self.set_extra_attributes(obj=user, attributes=extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser with the given email, username, and
        password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not (
            extra_fields.get("is_staff") and extra_fields.get("is_superuser")
        ):
            raise ValidationError(
                _("Superuser must have is_staff=True"),
                code="superuser_not_staff",
            )

        return self.create_user(email, username, password, **extra_fields)

    def deactivate_user(self, email):
        """Deactivate a user by setting their 'is_active' field to False.

        If no user is found, it raises a `User.DoesNotExist` exception.
        """
        try:
            self.set_user_active_status(email, is_active=False)
        except self.model.DoesNotExist as e:
            raise self.email_does_not_exist(email) from e

    def activate_user(self, email):
        """Activate a user by setting their 'is_active' field to True.

        If no user is found, it raises a `User.DoesNotExist` exception.
        """
        try:
            self.set_user_active_status(email, is_active=True)
        except self.model.DoesNotExist as e:
            raise self.email_does_not_exist(email) from e

    def set_user_active_status(self, email, is_active):
        """Updates the active status of a user.

        Args:
            email (str): The email of the user to update status for.
            is_active (bool): `True` or `False` to set the state.
        """
        user = self.get(email=email)
        user.is_active = is_active
        user.save(using=self._db, update_fields=["is_active"])

    def email_does_not_exist(self, email):
        """Raises an error when the email requested does not exist.

        Args:
            email (str): The email that wasn't found in the database.

        Raises:
            User.DoesNotExist: Raised because the provided email does exist in
            the list of available users in the database.
        """
        raise self.model.DoesNotExist(
            _(f"User with email: {email} does not exist.")
        )

    def update_user(self, email, **update_fields):
        """Update a user's information based on their email.

        The `updated_fields` argument contains the fields to update.
        If the user is not found, it raises a `User.DoesNotExist` exception.
        """
        try:
            user = self.get(email=email)
        except self.model.DoesNotExist as e:
            raise self.email_does_not_exist(email) from e
        else:
            user = self.set_extra_attributes(
                obj=user, attributes=update_fields
            )

            user.save(using=self._db)

    def set_extra_attributes(self, obj: object, attributes: dict):
        """Updates the `obj` with the attributes provided if they exist.

        obj (object): The object to set attributes for.
        attributes (dict): Key-value pairs of the attributes to set on the
        `obj`.

        Raises:
            AttributeError: When an attribute does exist on the `obj`.

        Returns:
            obj: The updated object when all the attributes are set correctly.
        """
        for attribute, value in attributes.items():
            if hasattr(obj, attribute):  # ensure the attribute exists
                setattr(obj, attribute, value)
            else:
                raise AttributeError(
                    _(
                        f"The attribute '{attribute}' does not exist on "
                        f"the {self.model.__name__} model."
                    )
                )

        return obj


class User(AbstractBaseUser):
    """User model."""

    class UserStation(models.TextChoices):
        """User station options."""

        WAREHOUSE = "WH", _("warehouse")
        SHOP = "SP", _("shop")

    id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True
    )
    username = models.CharField(
        max_length=255, unique=True, null=False, blank=False
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        blank=False,
        null=False,
    )
    password = models.CharField(max_length=255, blank=False, null=False)
    firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=False, null=False)
    role = models.OneToOneField(
        "Role", on_delete=models.SET_NULL, null=True, blank=True
    )
    organisation = models.OneToOneField(
        "Organisation", on_delete=models.CASCADE, null=True, blank=True
    )
    user_station = models.CharField(
        max_length=2, choices=UserStation, blank=False, null=False
    )
    station_id = models.UUIDField(blank=False, null=True)
    is_active = models.BooleanField(default=True, blank=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email",
        "firstname",
        "lastname",
        "role",
        "user_station",
    ]

    class Meta:
        """Metadata for the users model."""

        db_table = "users"
        indexes = [models.Index(fields=["id"])]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} with email: {self.email}"


class UserProfile(models.Model):
    """Defines the model that handles user profile and extra settings."""

    id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=False, blank=False
    )
    avatar = models.ImageField(upload_to="")

    class Meta:
        """Metadata for the user profiles model."""

        db_table = "profiles"


class Organisation(models.Model):
    """Defines the model that handles organisational logic.

    Organisations are used to group different users based on the company
    they work for. This ensures that users have access only to the
    specific organisation they belong and by extension enforces security
    at the organisation level.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=255, blank=False, null=False)
    logo = models.ImageField(upload_to="", null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="owner",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the organisations model."""

        db_table = "organisations"

    def __str__(self):
        return self.name


class Role(models.Model):
    """Defines the roles for users on the platform.

    This ensures that users have only the permissions they need for the
    actions the need to perform and nothing else. Essentially, this
    enforces the role-based access control (RBAC) of the system.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the roles model."""

        db_table = "roles"

    def __str__(self):
        return self.name


class Permission(models.Model):
    """A single permission to define what a user is allowed to do."""

    id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the permissions model."""

        db_table = "permissions"

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Handles the permissions for users."""

    id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        """Metadata for the role permissions model."""

        db_table = "role_permissions"
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"
