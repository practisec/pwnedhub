import graphene
from pwnedgraph.query import Query
from pwnedgraph.types import MessageType, UserType, RoomType

schema = graphene.Schema(query=Query, types=[MessageType, UserType, RoomType])
