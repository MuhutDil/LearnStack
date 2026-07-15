import redis
from django.conf import settings
from django.core.cache import cache
 
# # Setting up the Redis connection
# r = redis.Redis(
#     host=settings.REDIS_HOST,
#     port=settings.REDIS_PORT,
#     db=settings.REDIS_DB,
#     # decode_responses=True  # Automatically decode responses to strings
# )

 
def get_last_module_key(user_id, course_id):
    """
    Generate Redis key for storing last accessed module.
    Pattern: student:last_module:{user_id}:{course_id}
    """
    return f"student:last_module:{user_id}:{course_id}"


def save_last_accessed_module(user_id, course_id, module_id):
    """
    Save the last module a student accessed in a course.
    """
    key = get_last_module_key(user_id, course_id)
    cache.set(key, module_id)


def get_last_accessed_module(user_id, course_id):
    """
    Retrieve the last module a student accessed in a course.
    Returns module_id or None if not found.
    """
    key = get_last_module_key(user_id, course_id)
    module_id = cache.get(key)
    return module_id
