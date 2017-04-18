from django.db import models


class Department(models.Model):
    name = models.CharField(null=False, max_length=100, unique=True)


class RegionA(models.Model):
    name = models.CharField(null=False, max_length=100, unique=True)


class RegionB(models.Model):
    region_a = models.ForeignKey(RegionA)
    name = models.CharField(null=False, max_length=100, unique=True)
    code = models.IntegerField(null=False)


class SchoolType(models.Model):
    name_key = models.CharField(null=False, max_length=50)
    name_value = models.CharField(null=False, unique=True, max_length=50)


class UniversityType(models.Model):
    name = models.CharField(null=False, max_length=50, unique=True)


class University(models.Model):
    last_update = models.IntegerField(null=False, default=2017)
    code = models.IntegerField(null=False, unique=True)
    name = models.CharField(null=False, max_length=100, unique=True)
    university_type = models.ForeignKey(UniversityType)
    school_type = models.ForeignKey(SchoolType)
    region_a = models.ForeignKey(RegionA)
    region_b = models.ForeignKey(RegionB)
    domain = models.CharField(null=False, max_length=100)
