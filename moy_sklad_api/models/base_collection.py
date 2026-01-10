from pydantic import BaseModel


class BaseCollection[T: BaseModel](BaseModel):
    items: list[T]

    def all(self) -> list[T]:
        return self.items.copy()

    def first(self) -> T | None:
        if self.items:
            return self.items[0]
        return None
