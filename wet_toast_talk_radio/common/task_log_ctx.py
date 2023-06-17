import functools

from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
)


def task_log_ctx(task_name: str):
    def decorator_task_ctx(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            clear_contextvars()
            bind_contextvars(task=task_name)
            return func(*args, **kwargs)

        return wrapper_repeat

    return decorator_task_ctx
