from django.conf import settings
from django.core.paginator import Paginator


def get_page_obj(request, _list):
    paginator = Paginator(_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
