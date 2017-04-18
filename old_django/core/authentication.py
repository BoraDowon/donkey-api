from rest_framework.authentication import BaseAuthentication
from rest_framework import HTTP_HEADER_ENCODING, exceptions

from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache


def get_bora_authorization_header(request):
    auth = request.META.get('HTTP_X_AUTH_TOKEN', b'')
    if isinstance(auth, text_type):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class BoraApiAuthentication(BaseAuthentication):
    keyword = 'BoraToken'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    def authenticate_header(self, request):
        return self.keyword

    def authenticate(self, request):
        auth = get_bora_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()

        if cache.get(key):
            value_from_cache = cache.get(key)
            return value_from_cache['user'], key
        else:
            try:
                token = model.objects.get(key=key)
            except model.DoesNotExist:
                raise exceptions.AuthenticationFailed(_('Invalid token'))
            else:
                cache_data = {'user': token.user}
                cache.set(token.key, cache_data, 86400)

        return token.user, token
