from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        index=True
    )

    password = Column(String)

    customer = relationship(
        "Customer",
        back_populates="user",
        uselist=False
    )

    conversations = relationship(
        "Conversation",
        back_populates="user"
    )


class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    name = Column(String)

    email = Column(
        String,
        unique=True,
        index=True
    )

    user = relationship(
        "User",
        back_populates="customer"
    )

    orders = relationship(
        "Order",
        back_populates="customer"
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    product = Column(String)

    status = Column(String)

    customer = relationship(
        "Customer",
        back_populates="orders"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        String,
        unique=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(String)

    user = relationship(
        "User",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        String,
        ForeignKey("conversations.conversation_id"),
        index=True
    )

    role = Column(String)

    content = Column(String)

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

