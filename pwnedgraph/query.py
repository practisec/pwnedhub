import graphene
from graphql import GraphQLError
from pwnedgraph.types import MessageType, UserType, ToolType
from pwnedgraph.decorators import auth_required


class MessagesQuery(graphene.ObjectType):
    messages = graphene.List(MessageType)

    @auth_required
    def resolve_messages(self, info):
        query = MessageType.get_query(info)
        return query.all()


class MessageQuery(graphene.ObjectType):
    message = graphene.Field(MessageType, id=graphene.Int(required=True))

    @auth_required
    def resolve_message(self, info, **input):
        query = MessageType.get_query(info)
        result = query.filter(MessageType._meta.model.id == input.get('id')).first()
        if not result:
            raise GraphQLError('Message does not exist.')
        return result


class UsersQuery(graphene.ObjectType):
    users = graphene.List(UserType)

    @auth_required
    def resolve_users(self, info):
        query = UserType.get_query(info)
        return query.all()


class UserQuery(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))

    @auth_required
    def resolve_user(self, info, **input):
        query = UserType.get_query(info)
        result = query.filter(UserType._meta.model.id == input.get('id')).first()
        if not result:
            raise GraphQLError('User does not exist.')
        return result


class ToolsQuery(graphene.ObjectType):
    tools = graphene.List(ToolType)

    @auth_required
    def resolve_tools(self, info):
        query = ToolType.get_query(info)
        return query.all()


class Query(
    MessageQuery,
    MessagesQuery,
    UserQuery,
    UsersQuery,
    ToolsQuery,
    graphene.ObjectType):
    pass
