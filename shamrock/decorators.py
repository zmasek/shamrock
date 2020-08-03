"""Global Shamrock decorators """
import functools
import logging
from typing import Callable, Optional, Tuple

from .exceptions import ShamrockException
from .messages import EXCEPTION_ARGUMENT_VALUE

logger: logging.Logger = logging.getLogger(__name__)


def _check_argument_value(parameter: str, allowed_values: Tuple[str, ...]) -> Callable:
    """A decorator that checks the values of input parameters."""

    def decorator_check(func: Callable) -> Callable:
        @functools.wraps(func)
        def check_argument_value(*args, **kwargs) -> Callable:
            value: Optional[str] = args[
                1
            ] if func.__name__ == "plants_by" else kwargs.get(parameter)
            if value is not None and value not in allowed_values:
                values: str = " or ".join(
                    [f"'{allowed_value}'" for allowed_value in allowed_values]
                )
                message: str = EXCEPTION_ARGUMENT_VALUE.format(
                    parameter=parameter, values=values
                )
                logger.error(message)
                raise ShamrockException(message)
            return func(*args, **kwargs)

        return check_argument_value

    return decorator_check
