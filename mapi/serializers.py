from django.utils import timezone
from django.utils.translation import ugettext as _

from rest_framework import serializers

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard
from core.models.category import *

from mapi.models import Article
from mapi.models import ArticleReply


class ArticleSerializer(serializers.ModelSerializer):
    user_nickname = serializers.ReadOnlyField(source='user.nickname')

    article_title = serializers.SerializerMethodField('custom_board_title')
    article_content = serializers.SerializerMethodField('shorten_content')
    article_creation_time = serializers.SerializerMethodField('localtime_created_at')
    article_view_counts = serializers.ReadOnlyField(source='views')
    article_reported_counts = serializers.ReadOnlyField(source='yellow_cards')
    article_like_counts = serializers.ReadOnlyField(source='likes')

    class Meta:
        model = Article
        fields = (
            'id',
            'user_nickname',
            'article_title',
            'article_content',
            'article_view_counts',
            'article_reported_counts',
            'article_like_counts',
            'article_creation_time'
        )

    @staticmethod
    def custom_board_title(obj):
        if obj.status == 0:
            return obj.title
        if obj.status == 1:
            return _('신고된 글 입니다')
        if obj.status == 2:
            return _('삭제된 글 입니다')

    @staticmethod
    def localtime_created_at(obj):
        return timezone.localtime(obj.created_at)

    @staticmethod
    def shorten_content(obj):
        if obj.status == 0:
            return obj.content[:100]
        if obj.status == 1:
            return _('')
        if obj.status == 2:
            return _('')


class ArticleAddSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=DonkeyUser.objects.all())
    board = serializers.PrimaryKeyRelatedField(queryset=BulletinBoard.objects.all())

    class Meta:
        model = Article
        fields = (
            'id',
            'user',
            'board',
            'title',
            'content',
            'created_at',
            'modified_at',
            'views',
            'yellow_cards',
            'likes'
        )


class ArticleDetailSerializer(serializers.ModelSerializer):
    user_nickname = serializers.ReadOnlyField(source='user.nickname')

    article_title = serializers.ReadOnlyField(source='title')
    article_content = serializers.ReadOnlyField(source='content')
    article_creation_time = serializers.SerializerMethodField('localtime_created_at')
    article_modification_time = serializers.SerializerMethodField('localtime_modified_at')
    article_view_counts = serializers.ReadOnlyField(source='views')
    article_reported_counts = serializers.ReadOnlyField(source='yellow_cards')
    article_like_counts = serializers.ReadOnlyField(source='likes')

    class Meta:
        model = Article
        fields = (
            'id',
            'user_nickname',
            'article_title',
            'article_content',
            'article_creation_time',
            'article_modification_time',
            'article_view_counts',
            'article_reported_counts',
            'article_like_counts',
        )
        
    @staticmethod
    def localtime_created_at(obj):
        return timezone.localtime(obj.created_at)

    @staticmethod
    def localtime_modified_at(obj):
        return timezone.localtime(obj.modified_at)


class ArticleReplySerializer(serializers.ModelSerializer):
    user_nickname = serializers.ReadOnlyField(source='user.nickname')
    reply_content = serializers.SerializerMethodField('custom_content_name')
    reply_depth = serializers.ReadOnlyField(source='depth')
    reply_creation_time = serializers.SerializerMethodField('localtime_created_at')

    class Meta:
        model = ArticleReply
        fields = ('id', 'user_nickname', 'reply_content', 'reply_depth', 'reply_creation_time')

    @staticmethod
    def custom_content_name(obj):
        if obj.status == 0:
            return obj.content
        if obj.status == 1:
            return _('신고된 댓글 입니다')
        if obj.status == 2:
            return _('삭제된 댓글 입니다')

    @staticmethod
    def localtime_created_at(obj):
        return timezone.localtime(obj.created_at)


class DonkeyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonkeyUser
        fields = ('id', 'username', 'nickname', 'last_login')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class BulletinBoardSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField('board_id_link')

    class Meta:
        model = BulletinBoard
        fields = ('id', 'title', 'desc', 'link')

    @staticmethod
    def board_id_link(obj):
        return '/articles?board_id={}'.format(obj.id)
