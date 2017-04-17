from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from rest_framework.authtoken.models import Token

from treebeard.mp_tree import MP_Node

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Article(models.Model):
    user = models.ForeignKey(DonkeyUser, related_name='article', on_delete=models.CASCADE)
    board = models.ForeignKey(BulletinBoard)
    # status information
    # 0 - active ( viewing to user)
    # 1 - reported ( viewing to user but pre-defined masseage )
    # 2 - inactive ( not viewing to user )
    status = models.IntegerField(default=0)
    title = models.CharField(max_length=500)
    content = models.TextField(null=True)
    # TODO showing university logic needs to be implemented!
    #is_show_univ = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def increase_view_count(self):
        view = self.views
        self.views = view + 1
        self.save()

    class Meta:
        ordering = ["-created_at"]


class ArticleReply(MP_Node):
    article = models.ForeignKey(Article)
    user = models.ForeignKey(DonkeyUser)
    content = models.TextField(null=True)
    status = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
