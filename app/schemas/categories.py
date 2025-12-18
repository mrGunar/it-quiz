from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    category: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    category: str | None = None


class CategoryResponse(CategoryBase):
    id: int
    category: str

    model_config = ConfigDict(from_attributes=True)
