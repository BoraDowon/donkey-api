from django.core.management.base import BaseCommand
from core.models.category import *
from core.models.donkey_user import DonkeyUser
from core.models.connector import UserBoardConnector
from core.models.bulletin_board import BulletinBoard
import os


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    base = os.path.dirname(os.path.realpath(__file__))

    def _set_region_a(self):
        region_a = RegionA()
        region_a.name = '한국'
        region_a.save()

        r_a = RegionA()
        r_a.name = '미국'
        r_a.save()

    def _set_region_b(self):
        f = open(os.path.join(self.base, 'data_set/region_b.csv'), 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        for line in lines[1:]:
            tmp = line.split(',')
            region_b = RegionB()
            region_b.region_a = RegionA.objects.get(name='한국')
            region_b.name = tmp[0]
            region_b.code = int(tmp[1].replace('\t', ''))
            region_b.save()

    def _set_school_type(self):
        f = open(os.path.join(self.base, 'data_set/school_type.csv'), 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        for line in lines[1:]:
            tmp = line.split(',')
            s_type = SchoolType()
            s_type.name_key = tmp[0]
            s_type.name_value = tmp[1]
            s_type.save()

    def _set_university_type(self):
        f = open(os.path.join(self.base, 'data_set/university_type.csv'), 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        for line in lines[1:]:
            tmp = line.split(',')
            u_type = UniversityType()
            u_type.name = tmp[0]
            u_type.save()

    def _set_representative_university(self):
        f = open(os.path.join(self.base, 'data_set/RepresentativeUniversity.csv'), 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        for line in lines[1:]:
            tmp = line.split(',')
            if len(tmp) == 19:
                address = tmp[14]
            elif len(tmp) == 20:
                address = tmp[15]
            elif len(tmp) == 21:
                address = tmp[16]
            else:
                print(len(tmp))
                raise ValueError

            u = University()
            u.last_update = int(tmp[0])
            u.code = int(tmp[2])
            u.name = tmp[3]
            u.university_type = UniversityType.objects.get(name=tmp[4])
            u.school_type = SchoolType.objects.get(name_key=tmp[5])
            region_b = RegionB.objects.get(name=tmp[6])
            u.region_b = region_b
            u.region_a = region_b.region_a
            u.domain = address.replace('www.', '')
            u.save()

    def _create_default_bulletinboard(self):
        all_user_bulletinboard = BulletinBoard()
        all_user_bulletinboard.title = '모두의 게시판'
        all_user_bulletinboard.desc = 'access for all users'
        all_user_bulletinboard.save()

        univs = University.objects.all()
        for univ in univs:
            u = BulletinBoard()
            u.title = univ.name
            u.desc = '{} default board'.format(u.title)
            u.save()
            u.university.add(univ)


    def _service_model(self):
        self._set_region_a()
        self._set_region_b()
        self._set_school_type()
        self._set_university_type()
        self._set_representative_university()
        self._create_default_bulletinboard()

    def handle(self, *args, **options):
        self._service_model()
        #self._create_default_bulletinboard()
