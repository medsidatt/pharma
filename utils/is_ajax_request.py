
def is_ajax_request(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
