from attr import fields
from django.forms import models
from .models import FAQ, College, MenuItems, User, Restaurant, Review, Order, MenuItems, PaytmOrder, RestaurantSpecificInfo, PaytmOrderDetails, category
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db.models import Avg, F

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['is_admin', 'ver_code_update_time', 'ver_code']
        read_only_fields = ['is_vendor', 'is_verified', 'reward_points', 'referral_code']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).update(instance, validated_data=validated_data)

class RestaurantSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField('get_image_url', read_only=True)
    # phone = serializers.CharField(source = 'admin.phone', read_only=True)
    # email = serializers.EmailField(source = 'admin.email', read_only=True)
    rating = serializers.DecimalField(max_digits=4, decimal_places=1, read_only=True)
    # avg_rating = serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = ['name', 'tag_line', 'media', 'img_url', 'average_rating', 'id', 'restaurant_phone', 'restaurant_email', 'shopkeeper_status','rating']
        # read_only_fields = ['img_url', 'rating']
    # def get_avg_rating(self, obj):
    #     # for particular musician get all albums and aggregate the all stars and return the avg_rating
    #     return obj.Review_set.aggregate(avgs=Avg(F('rating'))).get('avgs',None)

    def get_image_url(self, obj):
        return obj.media.url


class RestaurantDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItems
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source = 'user_id.full_name', read_only=True)
    profile_pic = serializers.CharField(source = 'user_id.profile_picture', read_only=True)
    class Meta:
        model = Review
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format="%d %B %Y %I:%M %p")

    class Meta:
        model = Order
        fields = '__all__'
        depth = 2

class RestaurantItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItems
        fields = '__all__'

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'

class PaytmOrderSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format="%d %B %Y %I:%M %p")

    class Meta:
        model = PaytmOrder
        fields = '__all__'
        depth = 2

# An experiment to check how drf handles nested data
class NumberSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=50)

class ItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=100)
    item_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    item_serving = serializers.IntegerField()

class ResponseSerializer(serializers.Serializer):
    # numbers = NumberSerializer(many=True)
    items = ItemSerializer(many=True)
    amount = serializers.DecimalField(max_digits=6, decimal_places=2)
    order_mode = serializers.BooleanField()
    restaurant = serializers.IntegerField()
    order_schedule_date = serializers.DateTimeField()
    is_reward_applied = serializers.BooleanField()
    # email = serializers.CharField(max_length=50)
    # date = serializers.DateTimeField()

class RestaurantVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantSpecificInfo
        fields = '__all__'


class PaytmOrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaytmOrderDetails
        fields = '__all__'

class PaytmOrderItemSerializer(serializers.ModelSerializer):
    order_details = PaytmOrderDetailsSerializer(many = True, read_only = True)
    restaurant_name = serializers.CharField(source = 'restaurant', read_only=True)
    order_time = serializers.DateTimeField(source = 'order_date', format="%H:%M")
    order_date = serializers.DateTimeField(format="%d-%m-%Y")
    order_schedule_date = serializers.DateTimeField(format="%H:%M")
    class Meta:
        model = PaytmOrder
        fields = ['id','order_details', 'restaurant_name', 'order_date', 'order_amount','otp', 'order_schedule_date', 'order_mode', 'order_time']

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = category
        fields = '__all__'