import functools

from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
)


def task_log_ctx(task_name: str):
    """task_log_ctx is a class decorator that binds a task name to the logger contextvars.
    This makes every log message from the task include the task name as {task=<taskName>}
    """

    def decorator_task_ctx(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            clear_contextvars()
            bind_contextvars(task=task_name)
            return func(*args, **kwargs)

        return wrapper_repeat

    return decorator_task_ctx


def show_id_log_ctx():
    """task_log_ctx is a class decorator that binds a task name to the logger contextvars.
    This makes every log message from the task include the task name as {task=<taskName>}
    """

    def decorator_task_ctx(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            assert "show_id" in kwargs, "show_id must be provided"
            clear_contextvars()
            bind_contextvars(show_id=kwargs["show_id"])
            return func(*args, **kwargs)

        return wrapper_repeat

    return decorator_task_ctx
