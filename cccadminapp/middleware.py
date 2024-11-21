from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

class StoreLastVisitedURLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated and request.method == 'GET':
            current_url = resolve(request.path_info).url_name
            if current_url not in ['login', 'logout']:
                request.session['last_visited_url'] = request.path_info
        return response