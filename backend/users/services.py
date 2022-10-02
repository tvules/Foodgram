from rest_framework import exceptions


def clean_recipe_limit_param(request):
    request.GET = request.GET.copy()
    value = request.GET.get('recipes_limit')
    if value is not None:
        try:
            request.GET['recipes_limit'] = int(value)
        except ValueError:
            raise exceptions.ValidationError(
                {'recipes_limit': ['Incorrect type. Expected `int` value']}
            )
    return
