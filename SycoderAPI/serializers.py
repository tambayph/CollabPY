from rest_framework import serializers
from SycoderAPI.models import DryBulb, PagasaStn, Rainfall, SynopticData, Wind


class RainfallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rainfall
        fields = ["id", "stationNumber", "value", "valueType"]
        # fields = '__all__'


class WindSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wind
        fields = ["direction", "speed", "gust"]

class DryBulbSerializer(serializers.ModelSerializer):
    class Meta:
        model = DryBulb
        fields = ["value"]

class PagasaStnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagasaStn
        # fields = '__all__'

        fields = ["stn_number", "stn_name", "lat", "lon", ]


class SynopticDataSerializer(serializers.ModelSerializer):
    station = PagasaStnSerializer(read_only=True)
    # rainfall = RainfallSerializer(read_only=True)
    # wind = WindSerializer(read_only=True)
    # drybulb = DryBulbSerializer(read_only=True)

    class Meta:
        model = SynopticData
        fields = ["dateTimeUTC", "stationNumber", "station"]
        # fields = ["dateTimeUTC", "stationNumber", "station", "rainfall", "wind", "drybulb"]
        # read_only_fields = ["station", "rainfall", "wind", "drybulb"]
    # deep = 1