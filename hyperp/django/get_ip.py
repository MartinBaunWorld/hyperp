def get_ip(request):
    from hyperp import is_ip4
    for header in ["X-Real-IP", "X-Forwarded-For", "X-Forwarded-Host"]:
        if header in request.headers:
            ip = request.headers[header]

            if ',' in ip:
                ip = ip.split(',')[0]

            if not is_ip4(ip):
                continue

            return ip

    return "127.0.0.1"

