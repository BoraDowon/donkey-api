from django.http import HttpResponse
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import (api_view, permission_classes, authentication_classes)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import AnonymousUser
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.core import validators

from mapi.models import Article
from mapi.models import ArticleReply
from mapi.serializers import ArticleSerializer
from mapi.serializers import ArticleAddSerializer
from mapi.serializers import ArticleDetailSerializer
from mapi.serializers import ArticleReplySerializer
from mapi.serializers import DonkeyUserSerializer
from mapi.serializers import DepartmentSerializer
from mapi.serializers import BulletinBoardSerializer

from mapi.permissions import IsBoraApiAuthenticated
from mapi import permissions as bora_permissions

from mapi.errors import *

from core.json.response_wrapper import DonkeyJsonResponse
from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard
from core.models.connector import UserBoardConnector
from core.models.category import *
from core.utils import UserCrypto
from core.authentication import BoraApiAuthentication

from core.celery_email import Mailer
from core.utils import random_number

from celery import shared_task


def is_access_to_board(func):
    class Wrapper(object):
        def __init__(self):
            self.user_id = None
            self.board_id = None

        def __call__(self, *args, **kwargs):
            func(*args)

            user_board_connector = UserBoardConnector.objects.get(donkey_user_id=self.user_id)
            return user_board_connector.check_bulletinboard_id(self.board_id)
    return Wrapper()


@is_access_to_board
def check_board(user_id, board_id):
    check_board.user_id = user_id
    check_board.board_id = board_id


@shared_task()
def add(x, y):
    return x+y


@api_view(['POST'])
def celery_test(request):
    add.apply_async((10, 10),)

    return Response({'msg': 'success'})


@never_cache
@api_view(['GET'])
def pre_check(request):
    is_token_key = request.method == 'GET' and 'token' in request.GET
    if is_token_key:
        token = request.GET['token']

        if Token.objects.filter(key=token).exists():
            token = Token.objects.get(key=token)
            donkey_user = token.user
            donkey_user.update_last_login()
            res = {'msg': 'sucess',
                    'code': '200',
                    'data': {'result': True}}
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = {'msg': 'Invalid Token',
                    'code': '200',
                    'data': {'result': False}}

            return Response(res, status=status.HTTP_200_OK)
    else:
        res = {'msg': 'failed',
                'code': '200',
                'data': {'result': False}}
        return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def email_check(request):
    is_email = request.method == 'GET' and 'email' in request.GET
    if is_email:
        email = request.GET['email']

        try:
            validators.validate_email(email)
        except validators.ValidationError:
            res = {
                'code': '200',
                'msg': 'failed',
                'detail': 'Invalid email address',
                'data': {
                    'is_valid': False,
                    'msg': '잘못된 이메일',
                    'name': ''
                }
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            domain = email.split('@')[-1]
            try:
                university = University.objects.get(domain=domain)
            except University.DoesNotExist:
                res = {
                    'code': '200',
                    'msg': 'failed',
                    'detail': 'No service University',
                    'data': {
                        'is_valid': False,
                        'msg': '현재 서비스를 하지 않는 대학교',
                        'name': ''
                    }
                }

                return Response(res, status=status.HTTP_200_OK)
            else:
                res = {
                    'code': '200',
                    'msg': 'success',
                    'detail': 'Service University',
                    'data': {
                        'is_valid': True,
                        'msg': 'Service University',
                        'name': university.name
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

    else:
        res = {
            'code': '400',
            'msg': 'failed',
            'detail': 'No email field'
        }
        return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def gen_auth_key(request):
    is_email_key = request.method == 'GET' and 'email' in request.GET

    if is_email_key:
        key_email = request.GET['email']
        try:
            validators.validate_email(key_email)
        except validators.ValidationError:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid Email',
                'data': {
                    'is_sent': False,
                    'msg': '잘못된 이메일',
                }
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            if cache.get(key_email):
                res = {
                    'msg': 'failed',
                    'code': '200',
                    'detail': 'Processing authentication, check the email',
                    'data': {
                        'is_sent': True,
                        'msg': '이미 인증 메일이 발송되었습니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)
            else:
                auth_code = random_number()
                # TODO : when deply to real service, MUST BE CHANGED "1234" to auth_code
                cache_data = {'code': "1234", 'status': 'SENT', 'user_type': ''}
                cache.set(key_email, cache_data, timeout=300)
                #m = Mailer()
                #m.send_messages('Authorization Code', auth_code, [key_email])
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'authorization email is sent',
                    'data': {
                        'is_sent': True,
                        'msg': '인증 메일이 발송되었습니다',
                    }
                }

                return Response(res, status=status.HTTP_200_OK)
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def is_exist_user(request):
    crypto = UserCrypto()
    is_email_key = request.method == 'GET' and 'email' in request.GET
    is_authcode_key = request.method == 'GET' and 'auth_code' in request.GET

    if is_email_key and is_authcode_key:
        key_email = request.GET['email']
        auth_code = request.GET['auth_code']
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        res = {
            'msg': 'failed',
            'code': '200',
            'detail': 'There is no credential information in cache',
            'data': {
                'is_success': False,
                'is_exist': False,
                'msg': '재인증이 필요합니다',
            }
        }
        return Response(res, status=status.HTTP_200_OK)

    else:
        if auth_code == value_from_cache['code']:
            encrypted_email = crypto.encode(key_email)

            if DonkeyUser.objects.filter(email=encrypted_email).exists():
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'existed_user',
                    'data': {
                        'is_success': True,
                        'is_exist': True,
                        'msg': '기존의 사용자 입니다. 토큰을 재발행 할까요?',
                    }
                }
                return Response(res, status=status.HTTP_200_OK)
            else:
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'new_user',
                    'data': {
                        'is_success': True,
                        'is_exist': False,
                        'msg': '새로운 사용자입니다. 등록 진행합니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid authorization code',
                'data': {
                    'is_success': True,
                    'is_exist': False,
                    'msg': '잘못된 인증번호 입니다'
                }
            }
            return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def confirm_auth_key(request):
    crypto = UserCrypto()
    is_email_key = request.method == 'GET' and 'email' in request.GET
    is_authcode_key = request.method == 'GET' and 'auth_code' in request.GET

    if is_email_key and is_authcode_key:
        key_email = request.GET['email']
        auth_code = request.GET['auth_code']
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        res = {
            'msg': 'failed',
            'code': '200',
            'detail': 'There is no credential information in cache',
            'data': {
                'is_confirm': False,
                'msg': '재인증이 필요합니다',
            }
        }
        return Response(res, status=status.HTTP_200_OK)

    else:
        if auth_code == value_from_cache['code']:
            encrypted_email = crypto.encode(key_email)

            if DonkeyUser.objects.filter(email=encrypted_email).exists():
                user = DonkeyUser.objects.get(email=encrypted_email)
                token = Token.objects.get(user_id=user.id)
                # deleting caching
                if cache.get(token.key):
                    cache.delete(token.key)

                token.delete()
                new_token = Token.objects.create(user=user)
                cache.delete(key_email)

                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'existed_user',
                    'data': {
                        'is_confirm': True,
                        'is_exist': True,
                        'msg': '기존의 유저입니다',
                        'token': new_token.key
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

            else:
                value_from_cache['status'] = 'CONFIRM'
                value_from_cache['user_type'] = 'new_user'
                cache.set(key_email, value_from_cache, timeout=1800)
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'new_user',
                    'data': {
                        'is_confirm': True,
                        'is_exist': False,
                        'msg': '새로운 유저입니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid authorization code',
                'data': {
                    'is_confirm': False,
                    'msg': '잘못된 인증번호 입니다'
                }
            }
            return Response(res, status=status.HTTP_200_OK)

@cache_page(30)
@api_view(['GET'])
def get_departments(request):
    # Don't need to check request.method == 'GET'
    # Consider below way to reduce code lines
    '''
    key_email = request.GET.get('email', '')
    auth_code = request.GET.get('auth_code', '')
    if not key_email or not auth_code:
        res = {'msg': 'failed'}
    '''

    is_email_key = request.method == 'GET' and 'email' in request.GET
    is_authcode_key = request.method == 'GET' and 'auth_code' in request.GET

    if is_email_key and is_authcode_key:
        key_email = request.GET['email']
        auth_code = request.GET['auth_code']
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        res = {
            'msg': 'failed',
            'code': '200',
            'detail': 'There is no credential information in cache',
            'data': {
                'msg': '재인증이 필요합니다',
            }
        }
        return Response(res, status=status.HTTP_200_OK)
    else:
        if auth_code == value_from_cache['code']:
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
            res = {
                'msg': 'success',
                'code': '200',
                'detail': 'department information',
                'data': {
                    'department': serializer.data,
                }
            }
            return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid authorization code',
                'data': {
                    'msg': '잘못된 인증번호 입니다'
                }
            }
            return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['POST'])
def registration(request):
    is_email_key = request.method == 'POST' and 'email' in request.data
    is_authcode_key = request.method == 'POST' and 'auth_code' in request.data
    is_dept_id = request.method == 'POST' and 'department_id' in request.data
    if is_email_key and is_authcode_key and is_dept_id:
        key_email = request.data['email']
        auth_code = request.data['auth_code']
        dept_id = int(request.data['department_id'])
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        res = {
            'msg': 'failed',
            'code': '200',
            'detail': 'There is no credential information in cache',
            'data': {
                'is_register': False,
                'msg': '재인증이 필요합니다',
            }
        }
        return Response(res, status=status.HTTP_200_OK)

    else:
        if auth_code == value_from_cache['code']:
            # new user
            if value_from_cache['user_type'] == 'new_user':
                user = DonkeyUser()
                try:
                    user.user_save(key_email=key_email, department_id=dept_id)
                except validators.ValidationError as e:
                    res = {
                        'msg': 'failed',
                        'code': '200',
                        'detail': 'DonkeyUser: {}'.format(e),
                        'data': {
                            'is_register': False,
                            'msg': '현재 서비스를 하지 않는 대학교',
                        }
                    }
                    return Response(res, status=status.HTTP_200_OK)

                # bulletin searching
                joined_bulletins = BulletinBoard.objects.filter(university=user.university)
                _ = UserBoardConnector.objects.create(donkey_user=user)
                connector_btw_user_board = UserBoardConnector.objects.get(donkey_user=user)

                # default board
                connector_btw_user_board.set_bulletinboard_id(1)

                for bulletin in joined_bulletins:
                    connector_btw_user_board.set_bulletinboard_id(bulletin.id)

                token = Token.objects.get(user=user)
                cache.delete(key_email)
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'correctly data is saved in db',
                    'data': {
                        'is_register': True,
                        'token': token.key,
                        'msg': '성공적으로 가입 되었습니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid authorization code',
                'data': {
                    'is_register': False,
                    'msg': '잘못된 인증번호 입니다'
                }
            }
            return Response(res, status=status.HTTP_200_OK)


class InitDonkey(APIView):
    authentication_classes = (
        BoraApiAuthentication,
    )

    @method_decorator(never_cache)
    def get(self, request, format=None):
        if request.user == AnonymousUser():
            board_id = 1
            board = BulletinBoard.objects.filter(pk=1)
            serializer = BulletinBoardSerializer(board, many=True)

            res = {
                'msg': 'success',
                'code': '200',
                'detail': 'Anonymous User',
                'data': {
                    'is_anonymous': True,
                    'board': serializer.data,
                    'board_url': ['articles?board_id=1']
                }
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            board_ids = UserBoardConnector.objects.get(pk=request.user.id).get_bulletinboard_id()
            boards = []
            for board_id in board_ids:
                boards.append(BulletinBoard.objects.get(pk=board_id))

            serializer_board = BulletinBoardSerializer(boards, many=True)
            serializer_user = DonkeyUserSerializer(DonkeyUser.objects.get(id=request.user.id))
            res = {
                'msg': 'success',
                'code': '200',
                'detail': 'Current User',
                'data': {
                    'is_anonymous': False,
                    'board': serializer_board.data,
                    'user': serializer_user.data,
                }
            }
            return Response(res, status=status.HTTP_200_OK)


class ArticleList(APIView):
    permission_classes = (
        bora_permissions.ArticlesPermission,
    )
    authentication_classes = (
        BoraApiAuthentication,
    )

    @staticmethod
    def check_offset(offset_string):
        if offset_string == 'None':
            n_offset = 10
        else:
            try:
                n_offset = int(offset_string)
            except ValueError:
                return bad_request('Invalid Variables')
            else:
                if n_offset <= 0:
                    return bad_request('Invalid Variables')
                if n_offset > 100:
                    return bad_request('Invalid Variables')
        return n_offset

    @staticmethod
    def check_page(page_string):
        if page_string == 'None':
            n_page = 1
        else:
            try:
                n_page = int(page_string)
            except ValueError:
                return bad_request('Invalid Variables')
            else:
                if n_page <= 0:
                    return bad_request('Invalid Variables')
        return n_page

    @method_decorator(never_cache)
    def get(self, request, board_pk, format=None):
        try:
            board_id = int(board_pk)
        except (TypeError, ValueError):
            return bad_request('invalid variables')

        offset_check = request.GET.get('offset', 'None')
        n_offset = self.check_offset(offset_check)

        page_check = request.GET.get('page', 'None')
        n_page = self.check_page(page_check)

        if n_page == 1:
            try:
                first_id = Article.objects.filter(board_id=board_id).first().id
            except AttributeError:
                first_id = 0
        else:
            first_id_check = request.GET.get('last_id', 'None')
            if first_id_check == 'None':
                return bad_request('Invalid Variables')
            try:
                first_id = int(first_id_check)
            except ValueError:
                return bad_request('Invalid Variables')

        if first_id == 0:
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'empty article list',
            }
            return Response(res, status=status.HTTP_200_OK)

        n_start = (n_page-1) * n_offset
        n_end = n_page * n_offset
        articles = Article.objects.filter(board_id=board_id).filter(id__lte=first_id).all()[n_start:n_end]
        serializer = ArticleSerializer(articles, many=True)
        n_articles = len(articles)
        if n_articles != n_offset:
            # last or no article
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'articles list',
                'data': {
                    'articles': serializer.data,
                    'board_id': board_id,
                }
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            # general situation
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'articles list',
                'data': {
                    'articles': serializer.data,
                    'board_id': board_id,
                    'next_url': '/boards/{}?page={}&offset={}&last_id={}'
                        .format(board_id, n_page+1, n_offset, first_id)
                }
            }
            return Response(res, status=status.HTTP_200_OK)

    def post(self, request, board_pk, format=None):
        try:
            board_id = int(board_pk)
        except (TypeError, ValueError):
            return bad_request('invalid variables')

        request_data = request.data
        is_title = 'title' in request_data
        is_content = 'content' in request_data

        if is_title and is_content:
            items = request_data
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'Not enough fields',
            }
            return Response(res, status=status.HTTP_200_OK)

        items.update({'user': request.user.id})
        items.update({'board': board_id})

        serializer = ArticleAddSerializer(data=items)

        if serializer.is_valid():
            serializer.save()
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'article is saved',
                'data': {
                    'result': True,
                },
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'serializer validation is failed',
                'data': {
                    'result': False,
                }
            }
            return Response(res, status=status.HTTP_200_OK)


class ArticleDetail(APIView):
    permission_classes = (
        bora_permissions.ArticleDetailPermission,
    )
    authentication_classes = (
        BoraApiAuthentication,
    )

    @staticmethod
    def get_article(article_pk):
        is_query = False
        try:
            article = Article.objects.get(pk=article_pk)
        except Article.DoesNotExist:
            article = None
        else:
            is_query = True

        return is_query, article

    #@cache_page(60)
    @method_decorator(never_cache)
    def get(self, request, board_pk, article_pk, format=None):
        try:
            board_id = int(board_pk)
        except (TypeError, ValueError):
            return bad_request('invalid variables')

        is_query, article = self.get_article(article_pk)

        if is_query:
            # status checking 0: active, 1: reported, 2:inactive
            if article.status == 0:
                # board_id vs article.board_id checking
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

                if request.user.id != article.user_id:
                    article.increase_view_count()

                serializer = ArticleDetailSerializer(article)
                res = {
                    'code': '200',
                    'msg': 'success',
                    'detail': 'query ok',
                    'data': {
                        'article': serializer.data,
                        #'reply_link':
                    }
                }
                return Response(res, status=status.HTTP_200_OK)
            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)

    def delete(self, request, board_pk, article_pk, format=None):
        try:
            board_id = int(board_pk)
        except (TypeError, ValueError):
            return bad_request('invalid variables')

        is_query, article = self.get_article(article_pk)
        if is_query:
            if article.status == 0:
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)
                if request.user.id == article.user.id:
                    article.status = 2
                    article.save()
                    res = {
                        'code': '200',
                        'msg': 'success',
                        'detail': 'successfully deleted',
                        }

                    return Response(res, status=status.HTTP_200_OK)
                else:
                    # invalid access
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect article id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)
            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)

    def put(self, request, board_pk, article_pk, format=None):
        try:
            board_id = int(board_pk)
        except (TypeError, ValueError):
            return bad_request('invalid variables')

        request_data = request.data
        is_title = 'title' in request_data
        is_content = 'content' in request_data

        if is_title and is_content:
            items = request_data
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'Not enough fields',
            }
            return Response(res, status=status.HTTP_200_OK)

        is_query, article = self.get_article(article_pk)
        if is_query:
            if article.status == 0:
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

                if request.user.id == article.user.id:
                    items.update({'user': request.user.id})
                    items.update({'board': board_id})

                    serializer = ArticleAddSerializer(data=items)

                    if serializer.is_valid():
                        article.title = items['title']
                        article.content = items['content']
                        article.save()
                        res = {
                            'code': '200',
                            'msg': 'success',
                            'detail': 'article is successfully updated',
                            'data': {
                                'result': True,
                            },
                        }
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        res = {
                            'code': '400',
                            'msg': 'failed',
                            'detail': 'serializer validation is failed',
                            'data': {
                                'result': False,
                            }
                        }
                        return Response(res, status=status.HTTP_200_OK)

                else:
                    # invalid access
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect article id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)


class ArticleReplyList(APIView):
    permission_classes = (
        bora_permissions.ArticlesPermission,
    )

    authentication_classes(
        BoraApiAuthentication,
    )

    @staticmethod
    def integer_check(string_value):
        try:
            res = int(string_value)
        except (TypeError, ValueError):
            return bad_request('invalid variables')

        return res

    @staticmethod
    def get_article(article_pk):
        is_query = False
        try:
            article = Article.objects.get(pk=article_pk)
        except Article.DoesNotExist:
            article = None
        else:
            is_query = True

        return is_query, article

    @method_decorator(never_cache)
    def get(self, request, board_pk, article_pk, format=None):
        board_id = self.integer_check(board_pk)
        article_id = self.integer_check(article_pk)

        is_query, article = self.get_article(article_pk)
        if is_query:
            if article.status == 0:
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

                replies = ArticleReply.objects.filter(article_id=article_id).all()
                serializer = ArticleReplySerializer(replies, many=True)
                res = {
                    'code': '200',
                    'msg': 'success',
                    'detail': 'replies',
                    'data': {
                        'replies': serializer.data,
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)

    def post(self, request, board_pk, article_pk, format=None):
        board_id = self.integer_check(board_pk)
        article_id = self.integer_check(article_pk)

        request_data = request.data
        is_content = 'content' in request_data

        if is_content:
            content = request_data['content']
        else:
            return bad_request('not enough field data')

        is_query, article = self.get_article(article_pk)
        if is_query:
            if article.status == 0:
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

                reply = ArticleReply
                reply.add_root(
                    content=content,
                    article=Article.objects.get(pk=article_id),
                    user=DonkeyUser.objects.get(pk=request.user.id)
                )
                res = {
                    'code': '200',
                    'msg': 'success',
                    'detail': 'reply ok'
                }
                return Response(res, status=status.HTTP_200_OK)

            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)


class ArticleReplyDetail(APIView):
    permission_classes = (
        bora_permissions.ArticleReplyDetailPermission,
    )

    authentication_classes(
        BoraApiAuthentication,
    )

    @staticmethod
    def integer_check(string_value):
        try:
            res = int(string_value)
        except (TypeError, ValueError):
            return bad_request('invalid variables')

        return res

    @staticmethod
    def get_article(article_pk):
        is_query = False
        try:
            article = Article.objects.get(pk=article_pk)
        except Article.DoesNotExist:
            article = None
        else:
            is_query = True

        return is_query, article

    @staticmethod
    def get_reply(article_pk, reply_pk):
        is_query = False
        try:
            reply = ArticleReply.objects.filter(article_id=article_pk).get(pk=reply_pk)
        except ArticleReply.DoesNotExist:
            reply = None
        else:
            is_query = True

        return is_query, reply

    def post(self, request, board_pk, article_pk, reply_pk, format=None):
        board_id = self.integer_check(board_pk)
        article_id = self.integer_check(article_pk)
        reply_id = self.integer_check(reply_pk)

        request_data = request.data
        is_content = 'content' in request_data

        if is_content:
            content = request_data['content']
        else:
            return bad_request('not enough field data')

        is_query, article = self.get_article(article_pk)
        if is_query:
            if article.status == 0:
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

                is_reply_query, target_reply = self.get_reply(article_id, reply_id)
                if is_reply_query:
                    if target_reply.status == 0:
                        target_reply.add_child(
                            content=content,
                            article_id=article_id,
                            user_id=request.user.id
                        )
                        res = {
                            'code': '200',
                            'msg': 'success',
                            'detail': 'reply ok'
                        }
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        return bad_request('invalid access')
                else:
                    return bad_request('db does not reponse')

            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)

    def put(self, request, board_pk, article_pk, reply_pk, format=None):
        board_id = self.integer_check(board_pk)
        article_id = self.integer_check(article_pk)
        reply_id = self.integer_check(reply_pk)

        request_data = request.data
        is_content = 'content' in request_data

        if is_content:
            content = request_data['content']
        else:
            return bad_request('not enough field data')

        is_query, article = self.get_article(article_pk)
        if is_query:
            if article.status == 0:
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

                is_reply_query, target_reply = self.get_reply(article_id, reply_id)
                if is_reply_query:
                    if target_reply.user.id == request.user.id:
                        if target_reply.status == 0:
                            target_reply.content = content
                            target_reply.save()
                            res = {
                                'code': '200',
                                'msg': 'success',
                                'detail': 'reply successfully updated'
                            }
                            return Response(res, status=status.HTTP_200_OK)
                        else:
                            return bad_request('invalid access')
                    else:
                        res = {
                            'code': '400',
                            'msg': 'failed',
                            'detail': 'invalid request'
                        }
                        return Response(res, status=status.HTTP_200_OK)
                else:
                    return bad_request('db does not reponse')

            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)

    def delete(self, request, board_pk, article_pk, reply_pk, format=None):
        board_id = self.integer_check(board_pk)
        article_id = self.integer_check(article_pk)
        reply_id = self.integer_check(reply_pk)

        is_query, article = self.get_article(article_pk)
        if is_query:
            if article.status == 0:
                if board_id != article.board_id:
                    res = {
                        'code': '400',
                        'msg': 'failed',
                        'detail': 'invalid request (incorrect board id)'
                    }
                    return Response(res, status=status.HTTP_200_OK)

                is_reply_query, target_reply = self.get_reply(article_id, reply_id)
                if is_reply_query:
                    if target_reply.user.id == request.user.id:
                        if target_reply.status == 0:
                            target_reply.status = 2
                            target_reply.save()
                            res = {
                                'code': '200',
                                'msg': 'success',
                                'detail': 'reply successfully delete'
                            }
                            return Response(res, status=status.HTTP_200_OK)
                        else:
                            return bad_request('invalid access')
                    else:
                        res = {
                            'code': '400',
                            'msg': 'failed',
                            'detail': 'invalid request'
                        }
                        return Response(res, status=status.HTTP_200_OK)

                else:
                    return bad_request('db does not reponse')

            else:
                # invalid access
                res = {
                    'code': '400',
                    'msg': 'failed',
                    'detail': 'invalid request (incorrect article id)'
                }
                return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'db does not response'
            }
            return Response(res, status=status.HTTP_200_OK)


class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @method_decorator(never_cache)
    def get(self, request, format=None):
        user_id = int(request.user.id)
        try:
            donkey_user = DonkeyUser.objects.get(pk=user_id)
        except DonkeyUser.DoesNotExist:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'There is no user in db'
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            serializer = DonkeyUserSerializer(donkey_user)
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'User Information',
                'data': {
                    'user_info': serializer.data
                }
            }
            return Response(res, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        request_data = request.data
        is_nickname = 'nickname' in request_data

        if not is_nickname:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'Not enough data'
            }
            return Response(res, status=status.HTTP_200_OK)

        user_id = int(request.user.id)
        try:
            donkey_user = DonkeyUser.objects.get(pk=user_id)
        except DonkeyUser.DoesNotExist:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'There is no user in db'
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            donkey_user.nickname = request_data['nickname']
            donkey_user.save()
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'nickname is changed'
            }
            return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def hello(request):
    data = {'message': 'hello'}
    return DonkeyJsonResponse('200', 'success', 'success', data, status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
@authentication_classes((BoraApiAuthentication, ))
#@permission_classes((IsBoraApiAuthenticated, ))
def custom_auth_check(request):
    print(request.user)
    res = {
        'msg': 'success',
        'code': '200'
    }
    return Response(res, status=status.HTTP_200_OK)

