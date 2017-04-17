from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard
from core.models.connector import UserBoardConnector
from core.models.category import *

from mapi.errors import *


class IsBoraApiAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        is_auth = request.user and request.user.is_authenticated()
        return is_auth


class IsBoardOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
        try:
            board_id = request.GET['board_id']
        except KeyError:
            return False

        return user_board_connector.check_bulletinboard_id(board_id)


class ArticlesPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # access url variable by request
        # print('##', request.resolver_match.kwargs)
        if request.method == 'POST':
            try:
                user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
            except UserBoardConnector.DoesNotExist:
                return bad_request('Invalid variables')
            else:
                try:
                    board_id = int(request.resolver_match.kwargs.get('board_pk'))
                except (TypeError, ValueError):
                    return bad_request('Invalid variables')
                else:
                    user = DonkeyUser.objects.get(email=request.user)

            return not user.is_reported and user_board_connector.check_bulletinboard_id(board_id)

        if request.method == 'GET':
            try:
                board_id = int(request.resolver_match.kwargs.get('board_pk'))
            except (TypeError, ValueError):
                return bad_request('Invalid variables')
            else:
                if board_id == 1:
                    return True
                else:
                    if request.user == AnonymousUser():
                        return False
                    else:
                        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)

                        return user_board_connector.check_bulletinboard_id(board_id)


class ArticleDetailPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            board_id = int(request.resolver_match.kwargs.get('board_pk'))
        except (TypeError, ValueError):
            return bad_request('Invalid variables')

        if request.method == 'GET':
            if board_id == 1:
                return True
            # other board (ex. a default university bulletin board)
            else:
                if request.user == AnonymousUser():
                    return False
                else:
                    user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)

                    return user_board_connector.check_bulletinboard_id(board_id)

        if request.method in ['DELETE', 'PUT']:
            if request.user == AnonymousUser():
                return False
            else:
                user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
                return user_board_connector.check_bulletinboard_id(board_id)


class ArticleRepliesPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # access url variable by request
        # print('##', request.resolver_match.kwargs)
        if request.method == 'POST':
            try:
                user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
            except UserBoardConnector.DoesNotExist:
                return bad_request('Invalid variables')
            else:
                try:
                    board_id = int(request.resolver_match.kwargs.get('board_pk'))
                except (TypeError, ValueError):
                    return bad_request('Invalid variables')
                else:
                    user = DonkeyUser.objects.get(email=request.user)

            return not user.is_reported and user_board_connector.check_bulletinboard_id(board_id)

        if request.method == 'GET':
            try:
                board_id = int(request.resolver_match.kwargs.get('board_pk'))
            except (TypeError, ValueError):
                return bad_request('Invalid variables')
            else:
                if board_id == 1:
                    return True
                else:
                    if request.user == AnonymousUser():
                        return False
                    else:
                        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)

                        return user_board_connector.check_bulletinboard_id(board_id)


class ArticleReplyDetailPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            board_id = int(request.resolver_match.kwargs.get('board_pk'))
        except (TypeError, ValueError):
            return bad_request('Invalid variables')

        if request.method == 'GET':
            if board_id == 1:
                return True
            # other board (ex. a default university bulletin board)
            else:
                if request.user == AnonymousUser():
                    return False
                else:
                    user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)

                    return user_board_connector.check_bulletinboard_id(board_id)

        if request.method in ['DELETE', 'PUT', 'POST']:
            if request.user == AnonymousUser():
                return False
            else:
                user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
                return user_board_connector.check_bulletinboard_id(board_id)
