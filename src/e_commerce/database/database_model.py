from sqlalchemy.orm import(
    DeclarativeBase ,
    Mapped,
    mapped_column,
    
)
from sqlalchemy import Integer , Column , String , Text , ForeignKey , DateTime , Float

from datetime import UTC , datetime

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customer"

    id : Mapped[int] = mapped_column(Integer,primary_key=True,index=True,autoincrement=True)
    name : Mapped[str] = mapped_column(String, nullable=False)
    email : Mapped[str] = mapped_column(String,unique=True,nullable=False)
    address : Mapped[str] = mapped_column(String,nullable=False)

    

class Orders(Base):
    __tablename__ = "orders"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement = True)
    customer_id : Mapped[int] = mapped_column(ForeignKey("customer.id") , nullable=False )
    order_date : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default=lambda:datetime.now(UTC))
    total_amount : Mapped[float] = mapped_column(Float,nullable=False)

class Product(Base):
    __tablename__ = "products"

    id : Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    name : Mapped[str] = mapped_column(String,unique=True,nullable=False)
    price : Mapped[float] = mapped_column(Float,nullable=False)
    description : Mapped[str] = mapped_column(Text,nullable=False)


class OrderIteams(Base):
    __tablename__ = "order_iteams"

    id : Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    order_id : Mapped[int] = mapped_column(Integer,ForeignKey("orders.id"),nullable=False)
    product_id : Mapped[int] = mapped_column(Integer,ForeignKey("products.id"),nullable=False)
    quantity : Mapped[int] = mapped_column(Integer,nullable=False,default = 1)
