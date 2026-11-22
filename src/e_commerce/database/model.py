from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from datetime import UTC , datetime
import uuid

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    orders: Mapped[list["Orders"]] = relationship(back_populates="customer")

class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="orders")
    items: Mapped[list["OrderItems"]] = relationship(back_populates="order")

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_orders_total_amount_non_negative"),
    )

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    order_items: Mapped[list["OrderItems"]] = relationship(back_populates="product")

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
    )


class OrderItems(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    order: Mapped[Orders] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="order_items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
    )


class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name : Mapped[int] = mapped_column(String(100),nullable=False)
    hash_password : Mapped[int] = mapped_column(String(255),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default=lambda : datetime.now(UTC) , nullable=False)
    chat_session : Mapped[list["ChatSession"]] = relationship(back_populates="users", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_session"

    user_id : Mapped[int] = mapped_column(Integer,ForeignKey("users.id" , ondelete="CASCADE"),nullable=False , index=True)
    title : Mapped[str] = mapped_column(String(255), nullable=False , default="new chat")
    session_id : Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4 , primary_key=True )
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default=lambda : datetime.now(UTC) , nullable=False )
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default=lambda : datetime.now(UTC) , onupdate=lambda : datetime.now(UTC) , nullable=False )
    user : Mapped["User"] = relationship(back_populates="chat_session")
    messages: Mapped[list["ChatMessages"]] = relationship(back_populates="session",cascade="all, delete-orphan",order_by="ChatMessages.created_at")

class ChatMessages(Base):
    __tablename__ = "chat_messages"

    messages_id : Mapped[int] = mapped_column(Integer, primary_key=True ,autoincrement=True)
    session_id : Mapped[str] = mapped_column(String , ForeignKey("chat_session.session_id",ondelete="CASCADE") , nullable=False )
    role : Mapped[str] = mapped_column(String(20) , nullable=False)
    content : Mapped[str] = mapped_column(Text,nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default=lambda : datetime.now())
    session : Mapped["ChatSession"] = relationship(back_populates="messages")





