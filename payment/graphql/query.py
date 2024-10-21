import graphene

from payment.models import (
    User,
    Card,
    CardPaymentTransaction,
    PhonePaymentTransaction)
from payment.graphql.types import UserType, CardType, TransactionUnion


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    my_card = graphene.List(CardType)
    my_transactions = graphene.List(TransactionUnion)

    def resolve_all_users(self, info):
        return User.objects.all()

    def resolve_my_card(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not authenticated")
        my_cards = Card.objects.filter(user=user)
        return my_cards

    def resolve_my_transactions(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not authenticated")
        card_transactions = CardPaymentTransaction.objects.filter(user=user)
        phone_transactions = PhonePaymentTransaction.objects.filter(user=user)
        return list(card_transactions) + list(phone_transactions)