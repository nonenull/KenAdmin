def get_page(self):
    """
    A function which will be monkeypatched onto the request to get the current
    integer representing the current page.
    """
    try:
        return int(self.GET['page'])
    except (KeyError, ValueError, TypeError):
        return 1


def show_line(self):
    try:
        return int(self.GET['showLine'])
    except (KeyError, ValueError, TypeError):
        return 10


class PaginationMiddleware(object):
    """
    Inserts a variable representing the current page onto the request object if
    it exists in either **GET** or **POST** portions of the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.__class__.page = property(get_page)
        request.__class__.show_line = property(show_line)
        response = self.get_response(request)
        return response
