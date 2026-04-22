from pydantic import BaseModel

class TestBase(BaseModel):
    test_number: int
    id_discipline: int

class TestCreate(TestBase):
    pass

class TestOut(TestBase):
    id_test: int

    class Config:
        from_attributes = True