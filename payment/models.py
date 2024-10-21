from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models

from django.utils.translation import gettext_lazy as _

from payment.validator import card_number_validator


class CustomUserManager(BaseUserManager):
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser is is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser is is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def _create_user(self, phone_number, password, **extra_fields):
        user = self.model(phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)

    REQUIRED_FIELDS = []
    username = None

    EMAIL_FIELD = 'phone_number'
    USERNAME_FIELD = 'phone_number'

    objects = CustomUserManager()

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.phone_number}"


class Bank(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Card(models.Model):
    class CardType(models.TextChoices):
        HUMO = 'HUMO', _('Humo')
        UZCARD = 'UZCARD', _('UzCard')

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    card_number = models.CharField(max_length=16, unique=True, validators=[card_number_validator])
    card_type = models.CharField(max_length=6, choices=CardType.choices)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    expiration_date = models.CharField(max_length=5)
    currency = models.CharField(max_length=3, default="UZS")
    value = models.DecimalField(decimal_places=4, max_digits=15, default=0)

    def __str__(self):
        return f'{self.card_type} - {self.card_number}'


class MerchantCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class Merchant(models.Model):
    name = models.CharField(max_length=50)
    merchant_category = models.ForeignKey(MerchantCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    device_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.merchant.name} from {self.user.id}"


class PhonePaymentTransaction(Transaction):
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.phone_number}"


class CardPaymentTransaction(Transaction):
    card_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.card_number}"
