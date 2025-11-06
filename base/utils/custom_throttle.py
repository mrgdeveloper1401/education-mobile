from rest_framework.throttling import SimpleRateThrottle


class OtpRateThrottle(SimpleRateThrottle):
    scope = 'otp'

    def get_cache_key(self, request, view):
        mobile = request.data.get('mobile_phone')
        if not mobile:
            return None
        return self.cache_format % {'scope': self.scope, 'ident': mobile}
