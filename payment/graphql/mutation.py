from decimal import Decimal

import graphene
from django.db import transaction

from payment.models import (
    User,
    Card,
    CardPaymentTransaction,
    Merchant)
from payment.graphql.types import UserType, CardType, CardPaymentTransactionType, DecimalType


class CreateUser(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, info, phone_number, password):
        user = User.objects.create_user(phone_number=phone_number, password=password)
        return CreateUser(user=user)


class CreateCard(graphene.Mutation):
    class Arguments:
        card_type = graphene.String(required=True)
        card_number = graphene.BigInt(required=True)
        expiration_date = graphene.String(required=True)

    card = graphene.Field(CardType)

    @classmethod
    def mutate(cls, info, card_type, card_number, expiration_date):
        user = info.context.user
        card = Card(user=user, card_type=card_type, card_number=card_number, expiration_date=expiration_date)
        card.save()
        return CreateCard(card=card)


class CardTransaction(graphene.Mutation):
    class Arguments:
        card = graphene.BigInt(required=True)
        merchant = graphene.Int(required=True)
        amount = DecimalType(required=True)
        card_number = graphene.BigInt(required=True)

    card_transaction = graphene.Field(CardPaymentTransactionType)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, card, merchant, amount, card_number):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        try:
            card_instance = Card.objects.get(id=card, user=user)
        except Card.DoesNotExist:
            raise Exception("The card was not found or does not belong to the user")

        try:
            to_card = Card.objects.get(card_number=card_number)
        except Card.DoesNotExist:
            raise Exception("Destination card not found")

        if card_instance.value < amount:
            raise Exception("Insufficient balance")

        card_instance.value -= Decimal(amount)
        to_card.value += Decimal(amount)
        card_instance.save()
        to_card.save()

        device_id = info.context.META.get('HTTP_DEVICE_ID', '12345')

        try:
            merchant_instance = Merchant.objects.get(id=merchant)
        except Merchant.DoesNotExist:
            raise Exception("Merchant not found")

        transaction = CardPaymentTransaction(
            user=user,
            card=card_instance,
            merchant=merchant_instance,
            amount=amount,
            device_id=device_id,
            card_number=card_number
        )
        transaction.save()

        return CardTransaction(card_transaction=transaction)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_card = CreateCard.Field()
    card_transaction = CardTransaction.Field()
