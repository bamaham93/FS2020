from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps


def rate_limit(key_prefix="api", rate=60, per=60):
    """
    Simple rate limiting decorator.

    Args:
        key_prefix: Prefix for the cache key
        rate: Number of requests allowed
        per: Time period in seconds

    Usage:
        @rate_limit(key_prefix='bible_api', rate=100, per=60)
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get client IP
            ip = get_client_ip(request)
            cache_key = f"{key_prefix}:{ip}"

            # Get current request count
            request_count = cache.get(cache_key, 0)

            if request_count >= rate:
                return JsonResponse(
                    {
                        "error": "Rate limit exceeded. Please try again later.",
                        "limit": rate,
                        "period": per,
                    },
                    status=429,
                )

            # Increment counter
            cache.set(cache_key, request_count + 1, per)

            # Call the actual view
            response = view_func(request, *args, **kwargs)

            # Add rate limit headers
            response["X-RateLimit-Limit"] = str(rate)
            response["X-RateLimit-Remaining"] = str(rate - request_count - 1)

            return response

        return wrapper

    return decorator


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
