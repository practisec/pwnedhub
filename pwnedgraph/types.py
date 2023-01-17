from graphene_sqlalchemy import SQLAlchemyObjectType
from pwnedgraph.models import Scan, Membership, Note, Tool, Room, Message, User


class ScanType(SQLAlchemyObjectType):
    class Meta:
        model = Scan


class MembershipType(SQLAlchemyObjectType):
    class Meta:
        model = Membership


class NoteType(SQLAlchemyObjectType):
    class Meta:
        model = Note


class ToolType(SQLAlchemyObjectType):
    class Meta:
        model = Tool


class RoomType(SQLAlchemyObjectType):
    class Meta:
        model = Room


class MessageType(SQLAlchemyObjectType):
    class Meta:
        model = Message


class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User
