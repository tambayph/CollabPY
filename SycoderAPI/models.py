from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PagasaStn(models.Model):
    stn_number = models.CharField(primary_key=True, max_length=5)
    stn_name = models.CharField(max_length=255)
    lat = models.DecimalField(decimal_places=1, max_digits=4)
    lon = models.DecimalField(decimal_places=1, max_digits=4)
    island_category = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255)

    class Meta:
        # Set the table name
        db_table = 'pagasa_stn'
        managed = False

    def __str__(self):
        return self.stn_name


class SynopticData(BaseModel):
    id = models.AutoField(primary_key=True)
    dateTimeUTC = models.DateTimeField(auto_now=True)
    # stationNumber = models.CharField(max_length=50)
    stationNumber = models.OneToOneField(
        PagasaStn, on_delete=models.CASCADE, db_column="stationNumber", )
    blueprint = models.JSONField()
    savedBy = models.CharField(max_length=255)

    class Meta:
        db_table = 'synopticdata'
        managed = False

    def __str__(self):
        return self.blueprint


class Rainfall(BaseModel):
    id = models.IntegerField(primary_key=True)
    dateTimeUTC = models.DateTimeField()
    stationNumber = models.CharField(max_length=50)
    valueType = models.CharField(max_length=255)
    value = models.CharField(max_length=5)
    savedBy = models.CharField(max_length=255)
    rawSynopId = models.OneToOneField(SynopticData, on_delete=models.DO_NOTHING,
                                      db_column="rawSynopId", null=True, blank=True)  # type: ignore

    class Meta:
        db_table = 'Rainfall'
        managed = False

    def __str__(self):
        return self.stationNumber


class Wind(BaseModel):
    id = models.AutoField(primary_key=True)
    dateTimeUTC = models.DateTimeField()
    stationNumber = models.CharField(max_length=50)
    direction = models.CharField(max_length=50)
    speed = models.CharField(max_length=50)
    gust = models.CharField(max_length=50)
    savedBy = models.CharField(max_length=255)
    rawSynopId = models.OneToOneField(SynopticData, on_delete=models.DO_NOTHING,
                                      db_column="rawSynopId", null=True, blank=True)

    class Meta:
        db_table = 'winds'
        managed = False

    def __str__(self):
        return self.stationNumber


class DryBulb(BaseModel):
    id = models.AutoField(primary_key=True)
    dateTimeUTC = models.DateTimeField()
    stationNumber = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    rawSynopId = models.OneToOneField(SynopticData, on_delete=models.DO_NOTHING,
                                      db_column="rawSynopId", null=True, blank=True)

    class Meta:
        db_table = 'drybulbs'
        managed = False

    def __str__(self):
        return self.stationNumber
