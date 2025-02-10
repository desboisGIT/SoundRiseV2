from ipware import get_client_ip

def is_suspicious_ip(request):
    ip, _ = get_client_ip(request)
    suspicious_ips = ["192.168.1.1", "10.0.0.1"]  # Liste noire
    return ip in suspicious_ips
