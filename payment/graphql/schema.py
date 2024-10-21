import graphene

from payment.graphql.mutation import Mutation
from payment.graphql.query import Query

schema = graphene.Schema(query=Query, mutation=Mutation)
