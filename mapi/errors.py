from rest_framework import status
from rest_framework.response import Response


def bad_request(msg):
    res = {
        'msg': msg
    }

    return Response(res, status=status.HTTP_400_BAD_REQUEST)


def forbidden_request(msg):
    res = {
        'msg': msg
    }

    return Response(res, status=status.HTTP_403_FORBIDDEN)
