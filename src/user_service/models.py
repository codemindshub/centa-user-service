from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from uuid import uuid4


class CustomUserManager(BaseUserManager):
    """
    Custom manager for handling user creation and modification.

    Method(s):
        - create_user: Creates a new regular user.
        - create_superuser: Creates a new superuser with elevated permissions.
        - deactivate_user: Deactivates a user based on their email.
        - activate_user: Activates a user based on their email
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

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, username,
        and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, username, password, **extra_fields)

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
            raise self.model.DoesNotExist(f"User with email: {email} does not exist")


class User(AbstractBaseUser):
    class UserStation(models.TextChoices):
        WAREHOUSE = "WH", _("warehouse")
        SHOP = "SP", _("shop")

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    username = models.CharField(max_length=255, unique=True, null=False, blank=False)
    email = models.CharField(max_length=255, unique=True, blank=False, null=False, validators=[EmailValidator()])
    password = models.CharField(max_length=255, blank=False, null=False)
    firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=False, null=False)
    role = models.CharField(max_length=255, blank=False, null=False)
    organisation_id = models.OneToOneField(Organisation, on_delete=models.CASCADE, null=False, blank=False)
    user_station = models.CharField(max_length=2, choices=UserStation, blank=False, null=False)
    station_id = models.UUIDField(blank=False, null=True)
    is_active = models.BooleanField(default=True, blank=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "firstname", "lastname", "role", "user_station"]

    class Meta:
        db_table = "user"
        indexes = [models.Index(fields=["id"]),]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} with email: {self.email}"


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    avatar = models.ImageField(upload_to="")

    class Meta:
        db_table = "profiles"


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    logo = models.ImageField(upload_to="")
    address = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True, validators=[EmailValidator()])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organisation"

    def __str__(self):
        return self.name


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "role"

    def __str__(self):
        return self.name


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permission"

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = "role_permission"
        unique_together = ("role", "permission")

    def __str__(self):
i        return f"{self.role.name} - {self.permission.name}"
