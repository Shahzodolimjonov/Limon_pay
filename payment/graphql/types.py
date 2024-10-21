from decimal import Decimal

import graphene
from graphene_django.types import DjangoObjectType
from payment.models import (
    User,
    Card,
    Merchant,
    MerchantCategory,
    PhonePaymentTransaction,
    CardPaymentTransaction)


class DecimalType(graphene.Scalar):
    @staticmethod
    def serialize(value):
        return str(value)

    @staticmethod
    def parse_value(value):
        return Decimal(value)


class UserType(DjangoObjectType):
    class Meta:
        model = User


class CardType(DjangoObjectType):
    class Meta:
        model = Card


class MerchantType(DjangoObjectType):
    class Meta:
        model = Merchant


class MerchantCategoryType(DjangoObjectType):
    class Meta:
        model = MerchantCategory


class PhonePaymentTransactionType(DjangoObjectType):
    class Meta:
        model = PhonePaymentTransaction


class CardPaymentTransactionType(DjangoObjectType):
    class Meta:
        model = CardPaymentTransaction


class TransactionUnion(graphene.Union):
    class Meta:
        types = (CardPaymentTransactionType, PhonePaymentTransactionType)