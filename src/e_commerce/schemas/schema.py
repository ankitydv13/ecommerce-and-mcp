from datetime import datetime

from pydantic import BaseModel , Field , EmailStr , ConfigDict

class Customer(BaseModel):
    name : str = Field(..., min_length=3 , max_length=25)
    email : EmailStr = Field(max_length=30)
    address : str = Field(max_length=30)

    model_config = ConfigDict(from_attributes=True)

class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    address: str | None = None

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    total_amount: float = Field(ge=0)


class OrderUpdate(BaseModel):
    customer_id: int | None = Field(default=None, gt=0)
    total_amount: float | None = Field(default=None, ge=0)


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    order_date: datetime
    total_amount: float

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(ge=0)
    description: str


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price: float | None = Field(default=None, ge=0)
    description: str | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str

    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    order_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)


class OrderItemUpdate(BaseModel):
    order_id: int | None = Field(default=None, gt=0)
    product_id: int | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, gt=0)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)
    