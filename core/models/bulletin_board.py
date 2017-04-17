from django.db import models

from core.models.category import *


class BulletinBoard(models.Model):
    board_status = models.IntegerField(null=False, default=0)
    title = models.CharField(null=False, max_length=200)
    desc = models.CharField(null=False, max_length=300)
    region_a = models.ManyToManyField(RegionA, null=True)
    region_b = models.ManyToManyField(RegionB, null=True)
    university = models.ManyToManyField(University, null=True)
    department = models.ManyToManyField(Department, null=True)
    school_type = models.ManyToManyField(SchoolType, null=True)
    university_type = models.ManyToManyField(UniversityType, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
