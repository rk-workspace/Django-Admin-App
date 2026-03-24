from .models import RawMaterials, FinishedGoods, Compositions, JobCards, User
from rest_framework import serializers
import pyotp

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'is_staff', 'is_superuser', 'mfa_hash')

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.mfa_hash = pyotp.random_base32()
        user.save()
        return user




class RawMaterialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterials
        fields = ['id', 'rm_name', 'price', 'manufacturer', 'supplier', 'compliance', 'notes', 'description']


class FinishedGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinishedGoods
        fields = ['id', 'fg_name', 'customer', 'category', 'price', 'date', 'notes', 'composition_exists']


class CompositionsSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compositions
        fields = ['rm', 'quantity', 'fg', 'unit']


class CompositionServeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compositions
        fields = ['rm', 'quantity', 'fg', 'unit']
        depth = 1


class JobCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCards
        fields = ['id', 'date', 'issued_to', 'machine_no', 'fg', 'total_weight', 'no_of_batches']
