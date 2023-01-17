import graphene
from graphql import GraphQLError
from pwnedgraph import db
from pwnedgraph.types import MessageType, UserType
from pwnedgraph.decorators import auth_required
from pwnedgraph.models import Message as MessageModel, User as UserModel
from pwnedgraph.validators import is_valid_password
from pwnedgraph.utils import encode_jwt


class CreateMessage(graphene.Mutation):
    message = graphene.Field(MessageType)

    class Arguments:
        comment = graphene.String(required=True)
        room_id = graphene.Int(required=True)

    @auth_required
    def mutate(self, info, **input):
        comment = input.get('comment')
        room_id = input.get('room_id')
        new_message = MessageModel(
            comment=comment,
            author=info.context.user,
            room_id=room_id,
        )
        db.session.add(new_message)
        db.session.commit()
        return CreateMessage(message=new_message)


class DeleteMessage(graphene.Mutation):
    message = graphene.Field(MessageType)

    class Arguments:
        id = graphene.Int(required=True)

    @auth_required
    def mutate(self, info, **input):
        id = input.get('id')
        old_message = MessageModel.query.get(id)
        if not old_message:
            raise GraphQLError('Message does not exist.')
        if old_message.author != info.context.user and not info.context.user.is_admin:
            raise GraphQLError('Forbidden.')
        db.session.delete(old_message)
        db.session.commit()
        return DeleteMessage(message=old_message)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        name = graphene.String(required=True)
        avatar = graphene.String()
        signature = graphene.String()
        password = graphene.String(required=True)

    def mutate(self, info, **input):
        username = input.get('username')
        if UserModel.query.filter_by(username=username).first():
            raise GraphQLError('Username already exists.')
        email = input.get('email')
        if UserModel.query.filter_by(email=email).first():
            raise GraphQLError('Email already exists.')
        password = input.get('password')
        if not is_valid_password(password):
            raise GraphQLError('Password does not meet complexity requirements.')
        user = UserModel(**input)
        db.session.add(user)
        db.session.commit()
        return CreateUser(user=user)


class CreateToken(graphene.Mutation):
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, **input):
        username = input.get('username')
        password = input.get('password')
        user = UserModel.get_by_username(username)
        if user and not user.check_password(password):
            user = None
        if user and user.is_enabled:
            token = encode_jwt(user.id)
            return CreateToken(token=token)
        return GraphQLError('Invalid username or password.')


class Mutation(graphene.ObjectType):
    create_message = CreateMessage.Field()
    delete_message = DeleteMessage.Field()
    create_user = CreateUser.Field()
    create_token = CreateToken.Field()
