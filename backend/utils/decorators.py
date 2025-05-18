'''
Модуль для общих декораторов приложения.
'''
import functools
import logging
import inspect # Добавлено для проверки на асинхронные функции
from typing import Callable, Any

from backend.utils.exceptions import JivaPayException
# import backend.services.audit_logger as audit_logger # Пока не будем интегрировать напрямую, чтобы не усложнять

def handle_service_exceptions(logger: logging.Logger, service_name: str = "", success_level: int = logging.INFO, error_level: int = logging.ERROR, critical_level: int = logging.CRITICAL):
    """
    Декоратор для обработки исключений и логирования в сервисных функциях.
    Поддерживает как синхронные, так и асинхронные функции.

    Args:
        logger: Экземпляр логгера для записи сообщений.
        service_name: Опциональное имя сервиса/модуля для контекста в логах.
        success_level: Уровень логирования для успешного выполнения.
        error_level: Уровень логирования для ожидаемых ошибок (JivaPayException).
        critical_level: Уровень логирования для неожиданных ошибок (Exception).
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func_name = func.__name__
        log_prefix = f"{service_name}.{func_name}" if service_name else func_name

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                # logger.debug(f"{log_prefix} (async) - Called with args: {args}, kwargs: {kwargs}")
                try:
                    result = await func(*args, **kwargs)
                    if result is not None or logger.isEnabledFor(logging.DEBUG):
                        logger.log(success_level, f"{log_prefix} (async) - Successfully executed.")
                    return result
                except JivaPayException as e:
                    logger.log(error_level, f"{log_prefix} (async) - Service error: {e}", exc_info=True)
                    # Здесь можно добавить вызов audit_logger, если ошибка аудируемая
                    # Например: if isinstance(e, (AuthorizationError, NotFoundError)):
                    # audit_logger.log_event(..., details=str(e), level="WARNING" if isinstance(e, NotFoundError) else "ERROR")
                    raise # Перебрасываем ожидаемое исключение
                except Exception as e:
                    logger.log(critical_level, f"{log_prefix} (async) - Unexpected critical error: {e}", exc_info=True)
                    # audit_logger.log_event(..., action=f"{log_prefix.upper()}_UNEXPECTED_ERROR", details=str(e), level="CRITICAL")
                    raise # Перебрасываем неожиданное исключение
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                # logger.debug(f"{log_prefix} (sync) - Called with args: {args}, kwargs: {kwargs}")
                try:
                    result = func(*args, **kwargs)
                    if result is not None or logger.isEnabledFor(logging.DEBUG):
                        logger.log(success_level, f"{log_prefix} (sync) - Successfully executed.")
                    return result
                except JivaPayException as e:
                    logger.log(error_level, f"{log_prefix} (sync) - Service error: {e}", exc_info=True)
                    # Здесь можно добавить вызов audit_logger, если ошибка аудируемая
                    # Например: if isinstance(e, (AuthorizationError, NotFoundError)):
                    # audit_logger.log_event(..., details=str(e), level="WARNING" if isinstance(e, NotFoundError) else "ERROR")
                    raise # Перебрасываем ожидаемое исключение
                except Exception as e:
                    logger.log(critical_level, f"{log_prefix} (sync) - Unexpected critical error: {e}", exc_info=True)
                    # audit_logger.log_event(..., action=f"{log_prefix.upper()}_UNEXPECTED_ERROR", details=str(e), level="CRITICAL")
                    raise # Перебрасываем неожиданное исключение
            return sync_wrapper
    return decorator 