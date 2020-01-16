from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
# from phonenumber_field.modelfields import PhoneNumberField
from .manager import EmailUserManager


class EmailUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.

    """

    FOOD_TYPE = (
        ('V', 'Veg'),
        ('N', 'Non-veg'),
    )

    TIMMING = (
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
    )

    PAY = (
        ('M', 'Monthly'),
        ('W', 'Weekly'),
        ('O', 'Ontime'),
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    phone_number = models.CharField(_('Phone Number'),
                                    max_length=15,
                                    blank=True,
                                    null=True)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    tiffin_center_name = models.CharField(_('Tiffin center name'),
                                          max_length=300,
                                          blank=True)
    is_seller = models.BooleanField(_('is seller'), default=False)
    is_buyer = models.BooleanField(_('is buyer'), default=False)

    is_seller_approved = models.BooleanField(default=False)

    image = models.ImageField(upload_to='UserImages/', blank=True, null=True)
    food_type = models.CharField(max_length=1, choices=FOOD_TYPE)
    pay = models.CharField(max_length=1, choices=PAY)

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
