def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    real_ip = request.META.get('HTTP_X_REAL_IP')

    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
    elif real_ip:
        ip = real_ip
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip
