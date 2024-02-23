from typing import Callable, Generator

from .wrappers import Pagination, ApiPage, T, ApiList


def paginate(method: Callable[..., ApiPage[T]], *args, page=None,
             **kwargs) -> Generator[T, None, None]:
    next_pagination = Pagination(next_page=page)
    while True:
        wrapper = method(*args, page=next_pagination.next_page, **kwargs)

        if isinstance(wrapper, ApiPage):
            next_pagination = wrapper.pagination
        else:
            next_pagination = None

        if isinstance(wrapper, ApiPage) or isinstance(wrapper, ApiList):
            for item in wrapper.result:
                yield item
        else:
            raise ValueError("method does not support pagination")

        if not next_pagination or not next_pagination.next_page:
            break
