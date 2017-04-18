from rest_framework.response import Response


# FIXME
class DonkeyJsonResponse(Response):

    def __init__(self, code, msg, detail, data, status=None):
        result = {
            'code': code,
            'msg': msg,
            'detail': detail,
            'data': data
        }
        super(DonkeyJsonResponse, self).__init__(result, status=status)
