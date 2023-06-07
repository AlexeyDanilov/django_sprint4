from django.conf import settings
from django.core.paginator import Paginator


def get_page_objects(elements, page_number):
    paginator = Paginator(elements, settings.PAGE_ELEM)
    return paginator.get_page(page_number)
