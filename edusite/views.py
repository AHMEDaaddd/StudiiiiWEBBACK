from django.http import JsonResponse


def root_welcome(_request):
    return JsonResponse(
        {
            "message": "Добро пожаловать в edusite API",
            "endpoints": {
                "courses": "/api/courses/",
                "lessons": "/api/lessons/",
                "users": "/api/users/",
            },
        }
    )
