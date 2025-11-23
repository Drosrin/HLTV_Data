import functools
import time

def exponential_backoff(logger_getter=None, max_retries=5, exponential_wait_time=5.5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logger_getter(args[0]) if logger_getter else None
            retry_count = 0
            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if logger is not None:
                        logger.warning(f"An error occurred: {e}")
                        logger.warning(f"Retrying {func.__name__} ({retry_count}/{max_retries}) [Delayed Time = {exponential_wait_time} seconds]...")
                    time.sleep(exponential_wait_time * (2 ** retry_count))
                    retry_count += 1
            if logger is not None:
                logger.error(f"Max retries reached. Failed to execute {func.__name__}")
                logger.error("We might have been stuck by Cloudflare Turnstile!")
                logger.error("If this continuously happens, consider manual intervention. (Click that button!)")
                logger.error("It has been tested that proxy and VPN might trigger this.")
                logger.error("Consider turn it off.")
            return None
        return wrapper
    return decorator
