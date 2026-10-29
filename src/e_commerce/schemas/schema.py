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

class Orders(BaseModel):
    pass
    