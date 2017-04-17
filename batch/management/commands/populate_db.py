from django.core.management.base import BaseCommand
from core.models.category import *
from core.models.donkey_user import DonkeyUser
from core.models.connector import UserBoardConnector
from core.models.bulletin_board import BulletinBoard


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_test_univ(self):
        a = University()
        a.name = '보라대학교'
        a.domain = 'gmail.com'
        a.code = 9999
        a.university_type = UniversityType.objects.get(pk=1)
        a.school_type = SchoolType.objects.get(pk=4)
        a.region_a = RegionA.objects.get(pk=1)
        a.region_b = RegionB.objects.get(pk=1)

    def _create_test_dept(self):
        a = Department()
        a.name = '인문학'
        a.save()

        b = Department()
        b.name = '자연/공학'
        b.save()

        c = Department()
        c.name = '의치학과'
        c.save()

        d = Department()
        d.name = '예체능'
        d.save()

    def _create_univ(self):
        a = University()
        a.name = '에이대학교'
        a.domain = 'auniv.ac.kr'
        a.save()

        b = University()
        b.name = '비이대학교'
        b.domain = 'buniv.ac.kr'
        b.save()

        c = University()
        c.name = '씨이대학교'
        c.domain = 'cuniv.ac.kr'
        c.save()

        d = University()
        d.name = '디이대학교'
        d.domain = 'duniv.ac.kr'
        d.save()

    def _create_dept(self):
        a = Department()
        a.name = '인문학'
        a.save()

        b = Department()
        b.name = '자연/공학'
        b.save()

        c = Department()
        c.name = '의치학과'
        c.save()

        d = Department()
        d.name = '예체능'
        d.save()

    def _create_bulletinboard(self):
        univs = University.objects.all()
        for univ in univs:
            u = BulletinBoard()
            u.title = univ.name
            u.desc = univ.name
            u.save()
            u.university.add(univ)

        u = BulletinBoard()
        u.title = 'auniv/buniv'
        u.desc = 'a/b join'
        u.save()
        u.university.add(University.objects.get(domain='auniv.ac.kr'))
        u.university.add(University.objects.get(domain='buniv.ac.kr'))


    def _create_user(self):
        a = DonkeyUser()
        a.user_save(key_email='test1@auniv.ac.kr')
        c = UserBoardConnector()
        c.donkey_user = a
        c.save()
        joined = BulletinBoard.objects.filter(university=a.university)
        for j in joined:
            c.set_bulletinboard_id(j.id)

        a = DonkeyUser()
        a.user_save(key_email='test1@buniv.ac.kr')
        c = UserBoardConnector()
        c.donkey_user = a
        c.save()
        joined = BulletinBoard.objects.filter(university=a.university)
        for j in joined:
            c.set_bulletinboard_id(j.id)

        a = DonkeyUser()
        a.user_save(key_email='test1@cuniv.ac.kr')
        c = UserBoardConnector()
        c.donkey_user = a
        c.save()
        joined = BulletinBoard.objects.filter(university=a.university)
        for j in joined:
            c.set_bulletinboard_id(j.id)

        a = DonkeyUser()
        a.user_save(key_email='test1@duniv.ac.kr')
        c = UserBoardConnector()
        c.donkey_user = a
        c.save()
        joined = BulletinBoard.objects.filter(university=a.university)
        for j in joined:
            c.set_bulletinboard_id(j.id)

        a = DonkeyUser()
        a.user_save(key_email='test2@auniv.ac.kr')
        c = UserBoardConnector()
        c.donkey_user = a
        c.save()
        joined = BulletinBoard.objects.filter(university=a.university)
        for j in joined:
            c.set_bulletinboard_id(j.id)

    def handle(self, *args, **options):
        self._create_test_univ()
        self._create_test_dept()
        #self._create_univ()
        #self._create_dept()
        #self._create_bulletinboard()
        #self._create_user()
