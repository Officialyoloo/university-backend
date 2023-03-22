import datetime
from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string

from django.contrib.auth.hashers import make_password

from restaurants.models import FAQ, PaytmOrderDetails, Tax, User, Restaurant, MenuItems, Review, Order, College, PaytmOrder, category
from rest_framework import status
from restaurants.serializers import CategorySerializer, CollegeSerializer, FAQSerializer, PaytmOrderItemSerializer, PaytmOrderSerializer, RestaurantVerificationSerializer, UserSerializer,RestaurantDetailsSerializer, RestaurantSerializer, OrderSerializer, RestaurantItemSerializer, ResponseSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.db.models import Avg

import json
import random
from decimal import Decimal
from dateutil.tz import gettz
from django.contrib.auth import authenticate, login
import requests

from django.core.mail import EmailMultiAlternatives

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from restaurants.serializers import ReviewSerializer

import razorpay
import environ

from restaurants import Checksum

from channels.layers import get_channel_layer

channel_layer = get_channel_layer()
from asgiref.sync import async_to_sync

env = environ.Env()
environ.Env.read_env()

# customizing jwt claims
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims
#         token['profile_pic'] = user.profile_pic

#         return token

# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer

# customizing of jwt claims end


# Create your views here.
@api_view(['GET'])
def getAllUsers(request): #checked
    users = User.objects.all()
    serializedUsers = UserSerializer(users, many=True)
    return Response({"success":True, "users":serializedUsers.data})

@api_view(['POST'])
def userSignUp(request): #checked
    user = UserSerializer(data=request.data)
    if user.is_valid():
        user.save()
        return Response({"success":True,"user":user.data})
    else:
        return Response({"success":False, "errors":user.errors})

@api_view(['POST'])
def clientSignUp(request): #checked
    user = UserSerializer(data=request.data)
    if user.is_valid():
        user.validated_data['ver_code'] = random.randint(111111,999999)
        user.validated_data['is_active'] = False
        user.validated_data['is_verified'] = True #normal user don't need admin approval
        user.validated_data['referral_code'] = "qw"+user.validated_data['phone'][0:5]+"asd"+user.validated_data['phone'][5:]
        if 'reference_code' in user.validated_data and len(user.validated_data['reference_code'])>0:
            code = user.validated_data['reference_code']
            initial_length = len(code)
            new_code = ''.join(filter(str.isdigit, code))
            print(new_code)
            char_length = initial_length - len(new_code)
            if char_length == 5:
                try:
                    target_user = User.objects.filter(phone = new_code)[0]
                    target_user.reward_points += 10
                    target_user.save()
                except:
                    pass
        # user.validated_data['referral_code'] = random.randint(111111,999999)
        template = render_to_string(
                'email-verify.html', {'full_name': user.validated_data['full_name'], 'email': user.validated_data['email'], 'ver_code': user.validated_data['ver_code'], 'request':request})
        email = EmailMultiAlternatives(
            'Important: confirm your email address',
            template,
            settings.EMAIL_HOST_USER,
            [user.validated_data['email']],
        )
        email.attach_alternative(template, "text/html")
        email.fail_silently = False
        email.send()
        user.save()
        # we are generating reference code by concatenating random string of length 5 to user_id
        # user.referral_code = ''.join(random.choice(string.ascii_letters) for x in range(5))+str(user.data['id'])
        # user.save()
        return Response({"success":True,"user":user.data})
    else:
        return Response({"success":False, "errors":user.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def vendorSignUp(request): #checked
    user = UserSerializer(data=request.data)
    if user.is_valid():
        user.validated_data['ver_code'] = random.randint(111111,999999)
        user.validated_data['is_vendor'] = True
        user.validated_data['is_active'] = False
        template = render_to_string(
                'email-verify.html', {'full_name': user.validated_data['full_name'], 'email': user.validated_data['email'], 'ver_code': user.validated_data['ver_code']})
        email = EmailMultiAlternatives(
            'Important: confirm your email address',
            template,
            settings.EMAIL_HOST_USER,
            [user.validated_data['email']],
        )
        email.attach_alternative(template, "text/html")
        email.fail_silently = False
        email.send()
        user.save()
        return Response({"success":True,"user":user.data})
    else:
        return Response({"success":False, "errors":user.errors}, status=status.HTTP_400_BAD_REQUEST)

# Admin should either be created via terminal or some admin can make normal user admin, there should be no direct api for creating admin
# @api_view(['POST'])
# def adminSignUp(request):
#     user = UserSerializer(data=request.data)
#     if user.is_valid():
#         user.validated_data['is_verified'] = True
#         user.validated_data['is_admin'] = True
#         user.save()
#         return Response({"success":True,"user":user.data})
#     else:
#         return Response({"success":False, "errors":user.errors})

@api_view(['GET'])
def verifyEmail(request, email, code): #checked
    # code = request.data['ver_code']
    # email = request.data['email']
    user = User.objects.get(email=email)
    if user.ver_code == code:
        user.is_active = True
        user.save()
        return Response({"success":True})
    else:
        return Response({"success":False})

@api_view(['POST'])
def clientLogin(request): #checked
    phone = request.data['phone'] #phone number
    password = request.data['password']
    user = authenticate(username=phone, password=password)
    if user is not None:
        # login(request, user)
        # print(user.is_active,"ppp")
        url = request.scheme+"://"+request.META['HTTP_HOST']+'/api/token/'
        obj = {
            "phone":phone,
            "password":password
        }
        a = requests.post(url, obj)
        a = a.json()
        a['user_id'] = user.id
        if user.profile_picture:
            a["profile_picture"] = user.profile_picture.url
        else:
            a["profile_picture"] = None
        # if user.is_active and not user.is_vendor:
        #     return Response(a)
        # The above 2 lines of code made sure that only client/normal people can login to order wala interface but now we allow all to login there
        if user.is_active:
            return Response(a)
    return Response({"success":False}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def vendorLogin(request): #checked 
    phone = request.data['phone'] #phone number
    password = request.data['password']
    user = authenticate(username=phone, password=password)
    if user is not None:
        # login(request, user)
        url = request.scheme+"://"+request.META['HTTP_HOST']+'/api/token/'
        obj = {
            "phone":phone,
            "password":password
        }
        a = requests.post(url, obj)
        a = a.json()
        if user.is_active and user.is_vendor and user.is_verified:
            return Response(a)
        else:
            return Response({"success":False, "error":"User's might not be verified or it is not verified by admin"})
    return Response({"success":False}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def forgotPasswordMailer(request): # checked but email message body is to be changed, like when user will click that link, it will be redirected to react page with some payload(code and email), and after that he enter the old-new password and send it to forgotPasswordHandler function
    try:
        email = request.data['email']
    except:
        return Response({"success":False, "error":"email is required field"})
    try:
        user = User.objects.get(email=email)
    except:
        return Response({"success":True}) #confuse the attacker
    user.ver_code = random.randint(111111,999999)
    template = render_to_string(
                'password-reset.html', {'full_name': user.full_name, 'email': user.email, 'ver_code': user.ver_code})
    email = EmailMultiAlternatives(
        'Important: confirm your email address',
        template,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(template, "text/html")
    email.fail_silently = False
    email.send()
    user.save()
    return Response({"success":True})

@api_view(['POST'])
def forgotPasswordHandler(request): #checked
    try:
        email = request.data['email']
        code = int(request.data['code'])
        new_password = request.data['new_password']
    except:
        return Response({"success":False, "error":"following fields are required - email,code and new_password"})
    try:
        user = User.objects.get(email=email)
    except:
        return Response({"success":False})
    timeElapsed = datetime.datetime.now(tz=gettz('Asia/Kolkata'))-user.ver_code_update_time
    timeElapsedInSeconds = timeElapsed.total_seconds()
    if timeElapsedInSeconds<=600 and user.ver_code == code: #time taken is less then 10 minutes
        #kuch acha password setting method
        user.password = make_password(new_password)
        user.ver_code *= 10 #so that same link can't be reused within 10 seconds
        user.save()
        return Response({"success":True})
    else:
        return Response({"success":False, "error":f"You have reached after {timeElapsedInSeconds} seconds"})



# we can have one more field in user-model by label isVendor and other as status which is by default true but not for vendor
# the normal login can be done by all(admin, vendor and normal users)
# the vendor login will first check if the credentials corresponds to a vendor then only it allows to head to it's portal
# admin portal is as always separate(django's default admin panel)

# vendor login krk ek restaurant form bhr skta h jisko admin approve krega
@api_view(["GET"]) #checked
def listRestaurants(request,college_id):
    college = College.objects.filter(id=college_id)[0]
    all_restaurants = Restaurant.objects.filter(college=college).annotate(rating=Avg('review__rating'))
    restaurants = RestaurantSerializer(all_restaurants, many = True)
    return Response(restaurants.data)

@api_view(["GET"]) #checked
def restaurantDetails(request, id:int):
    restaurant = MenuItems.objects.filter(restaurant_id=id)
    menu = RestaurantDetailsSerializer(restaurant, many = True)
    return Response(menu.data)

@api_view(["POST"])
def sendRatings(request):
    rating = ReviewSerializer(data = request.data)
    if rating.is_valid():
        rating.save()
        return Response({"success":True})
    else:
        return Response({"success":False, "error":rating.errors})

@api_view(["GET"])
def showRatings(request,restId):
    ratings = Review.objects.filter(restaurant = restId)
    data = ReviewSerializer(ratings, many=True)
    return Response(data.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getClientDetails(request):
    client = User.objects.get(phone = request.user.phone)
    data = UserSerializer(client)
    return Response(data.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def getReviewsByUser(request):
    reviews = Review.objects.filter(user_id = request.user)
    # print(len(reviews), "popt2t")
    data = ReviewSerializer(reviews, many=True)
    return Response(data.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def updateClientProfile(request):   #can only update name and profile pic
    client = User.objects.get(phone = request.user.phone)
    serializer = UserSerializer(client, data = request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def updateRestaurantProfile(request):
    restaurant = Restaurant.objects.filter(admin=request.user)[0]
    # client = User.objects.get(phone = request.user.phone)
    serializer = RestaurantSerializer(restaurant, data = request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_payment(request):
    # request.data is coming from frontend
    amount = request.data['amount']
    name = request.data['name']
    restaurant_id = request.data['restaurant_id']
    phone = request.data['phone']
    order_mode = request.data['order_mode']

    # setup razorpay client this is the client to whome user is paying money that's you
    client = razorpay.Client(auth=(env('PUBLIC_KEY'), env('SECRET_KEY')))

    # create razorpay order
    # the amount will come in 'paise' that means if we pass 50 amount will become
    # 0.5 rupees that means 50 paise so we have to convert it in rupees. So, we will 
    # mumtiply it by 100 so it will be 50 rupees.
    payment = client.order.create({"amount": int(amount) * 100, 
                                   "currency": "INR", 
                                   "payment_capture": "1"})

    # we are saving an order with isPaid=False because we've just initialized the order
    # we haven't received the money we will handle the payment succes in next 
    # function
    order = Order.objects.create(order_product=name, 
                                 order_amount=amount, 
                                 order_payment_id=payment['id'],
                                 restaurant_id_id=restaurant_id,
                                 Orderer_id=request.user,
                                 order_mode=order_mode)

    serializer = OrderSerializer(order)

    """order response will be 
    {'id': 17, 
    'order_date': '23 January 2021 03:28 PM', 
    'order_product': '**product name from frontend**', 
    'order_amount': '**product amount from frontend**', 
    'order_payment_id': 'order_G3NhfSWWh5UfjQ', # it will be unique everytime
    'isPaid': False}"""

    data = {
        "payment": payment,
        "order": serializer.data
    }
    return Response(data)


@api_view(['POST'])
def handle_payment_success(request):
    # request.data is coming from frontend
    res = json.loads(request.data["response"])

    """res will be:
    {'razorpay_payment_id': 'pay_G3NivgSZLx7I9e', 
    'razorpay_order_id': 'order_G3NhfSWWh5UfjQ', 
    'razorpay_signature': '76b2accbefde6cd2392b5fbf098ebcbd4cb4ef8b78d62aa5cce553b2014993c0'}
    this will come from frontend which we will use to validate and confirm the payment
    """

    ord_id = ""
    raz_pay_id = ""
    raz_signature = ""

    # res.keys() will give us list of keys in res
    for key in res.keys():
        if key == 'razorpay_order_id':
            ord_id = res[key]
        elif key == 'razorpay_payment_id':
            raz_pay_id = res[key]
        elif key == 'razorpay_signature':
            raz_signature = res[key]

    # get order by payment_id which we've created earlier with isPaid=False
    order = Order.objects.get(order_payment_id=ord_id)

    # we will pass this whole data in razorpay client to verify the payment
    data = {
        'razorpay_order_id': ord_id,
        'razorpay_payment_id': raz_pay_id,
        'razorpay_signature': raz_signature
    }

    client = razorpay.Client(auth=(env('PUBLIC_KEY'), env('SECRET_KEY')))

    # checking if the transaction is valid or not by passing above data dictionary in 
    # razorpay client if it is "valid" then check will return None
    check = client.utility.verify_payment_signature(data)

    if check is not None:
        print("Redirect to error url or error page")
        return Response({'error': 'Something went wrong'})

    # if payment is successful that means check is None then we will turn isPaid=True
    order.isPaid = True
    order.save()

    res_data = {
        'message': 'payment successfully received!'
    }

    return Response(res_data)

@api_view(['GET'])
def getColleges(request):
    colleges = College.objects.all()
    serialized_colleges = CollegeSerializer(colleges, many=True)
    return Response({'colleges':serialized_colleges.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addFoodItems(request):
    # print(request.user.phone)
    item = RestaurantItemSerializer(data = request.data)
    if item.is_valid():
        item.save()
        return Response(item.data)
    else:
        return Response(item.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOwnRestaurantMenu(request):
    # print(request.META['HTTP_HOST'])
    # print(request.scheme+"://"+request.META['HTTP_HOST'])
    restaurant = Restaurant.objects.filter(admin=request.user)[0]
    Items = MenuItems.objects.filter(restaurant=restaurant)
    seriealized_items = RestaurantDetailsSerializer(Items, many=True)
    return Response({"menu":seriealized_items.data, "restaurant_id":restaurant.id})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getOrderHistory(request):   # list of orders
#     orders = Order.objects.filter(Orderer_id=request.user)
#     serialized_orders = OrderSerializer(orders, many=True)
#     return Response(serialized_orders.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteItem(request):
    id = request.data['id']
    item = MenuItems.objects.get(id=id)
    item.delete()
    return Response({"success":True})

# @api_view(['POST'])
# def getHotelByCollege(request):
#     college_id = request.data['id']
#     college = College.objects.filter(id=college_id)[0]
#     hotels = Hotel.objects.filter(college = college)
#     hotel_serializer = HotelSerializer(hotels, many=True)
#     return Response({"success":True, 'data':hotel_serializer.data})

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def paytm_start_payment(request):
    # request.data is coming from frontend
    amount = request.data['amount']
    # name = request.data['name']
    # email = request.data['email']
    # restaurant_id = request.data['restaurant_id']
    # print("HaaaaaaahaHaaaaaaa", request.data['random_object'], type(request.data['random_object']))
    # print(json.loads(request.data['random_object']))
    sz1 = ResponseSerializer(data = request.data)
    print(sz1.is_valid())
    print(sz1.errors)
    # print(sz1.data['order_schedule_date'])

    # we are saving an order instance (keeping isPaid=False)
    order = PaytmOrder.objects.create(order_amount=sz1.data["amount"],
                                 user=request.user,
                                 restaurant_id=sz1.data["restaurant"],
                                 order_schedule_date =sz1.data['order_schedule_date'],
                                 order_mode = sz1.data['order_mode'],
                                 otp=random.randint(1111,9999) )
    
    items = sz1.data['items']
    actual_total_price = 0
    for item in items:
        item_id = item['item_id']
        dish = MenuItems.objects.get(id=item_id)
        actual_total_price += dish.price*item['item_serving']
        PaytmOrderDetails.objects.create(item_name=dish.dish_name, item_price=dish.price, item_serving=item['item_serving'], order_id=order.id)
    
    tax = Tax.objects.all()[0]
    order.order_amount = actual_total_price*(1+tax.tax_percent*Decimal('0.01'))
    if(sz1.data['is_reward_applied']):
        if(order.order_amount>request.user.reward_points):
            amount_to_deduct = request.user.reward_points
            request.user.reward_points = 0
            request.user.save()
        else:
            amount_to_deduct = int(order.order_amount - 1)
            request.user.reward_points -= int(order.order_amount - 1)
            request.user.save()
        order.order_amount = order.order_amount - amount_to_deduct
    TXN_AMOUNT = "{:.2f}".format(order.order_amount)
    print(TXN_AMOUNT)
    order.save()

    # serializer = PaytmOrderSerializer(order)
    # we have to send the param_dict to the frontend
    # these credentials will be passed to paytm order processor to verify the business account
    param_dict = {
        'MID': env('MERCHANTID'),
        'ORDER_ID': str(order.id),
        'TXN_AMOUNT': TXN_AMOUNT,
        'CUST_ID': "random@gmail.com",
        'INDUSTRY_TYPE_ID': 'Retail',
        'WEBSITE': 'DEFAULT',
        'CHANNEL_ID': 'WEB',
        'CALLBACK_URL': 'https://'+ request.META['HTTP_HOST'] +'/paytm-handlepayment/',
        # this is the url of handlepayment function, paytm will send a POST request to the fuction associated with this CALLBACK_URL
    }

    # create new checksum (unique hashed string) using our merchant key with every paytm payment
    param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, env('MERCHANTKEY'))
    # send the dictionary with all the credentials to the frontend
    return Response({'param_dict': param_dict})


@api_view(['POST'])
def paytm_handlepayment(request):
    checksum = ""
    # the request.POST is coming from paytm
    form = request.POST

    response_dict = {}
    order = None  # initialize the order varible with None

    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            # 'CHECKSUMHASH' is coming from paytm and we will assign it to checksum variable to verify our paymant
            checksum = form[i]

        if i == 'ORDERID':
            # we will get an order with id==ORDERID to turn isPaid=True when payment is successful
            order = PaytmOrder.objects.get(id=form[i])

    # print(response_dict)

    # we will verify the payment using our merchant key and the checksum that we are getting from Paytm request.POST
    verify = Checksum.verify_checksum(response_dict, env('MERCHANTKEY'), checksum)

    if verify:
        if response_dict['RESPCODE'] == '01':
            # if the response code is 01 that means our transaction is successfull
            print('order successful')
            # after successfull payment we will make isPaid=True and will save the order
            order.isPaid = True
            order.save()

            async_to_sync(channel_layer.group_send)("restaurant_1", {"type": "chat_message", "message": "New order!!!"})

            # we will render a template to display the payment status
            return render(request, 'paytm/paymentstatus.html', {'response': response_dict})
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
            return render(request, 'paytm/paymentstatus.html', {'response': response_dict})

@api_view(["POST"])
def orderVerifier(request): #this api would be used when user will collect food from restaurant
    # print(request.data)
    try:
        otp = request.data['otp']
        order_id = request.data['order_id']
    except:
        return Response({"success":False, "message":"either otp or order_id is missing"})
    try:
        order = PaytmOrder.objects.get(id=order_id)
    except:
        return Response({"success":False, "message":"Invalid order_id"})
    if(order.otp==int(otp)):
        order.is_completed = True
        order.save()
        return Response({"success":True})
    else:
        return Response({"success":False, "message":"Incorrect OTP"})

@api_view(['GET'])
def searchByRestaurantAndMenu(request, college_id, search_term):
    restaurants = Restaurant.objects.filter(college = college_id, name__istartswith = search_term).annotate(rating=Avg('review__rating'))
    # restaurants = restaurants.objects.filter()
    menu_items = MenuItems.objects.filter(restaurant__college = college_id, dish_name__istartswith = search_term)
    # menu_items = menu_items.objects.filter()
    restaurants = RestaurantSerializer(restaurants, many=True)
    menu_items = RestaurantItemSerializer(menu_items, many= True)
    return Response({"Restaurants":restaurants.data, "Menu":menu_items.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def RestaurantVerifcationInfo(request):
    rest_info = RestaurantVerificationSerializer(data = request.data)
    if rest_info.is_valid():
        rest_info.save()
        return Response(rest_info.data)
    else:
        return Response(rest_info.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkin_checkout(request, rest_id):
    restaurant = Restaurant.objects.get(id=rest_id)
    restaurant.shopkeeper_status = 1-restaurant.shopkeeper_status
    restaurant.save()
    return Response({'status':restaurant.shopkeeper_status})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def client_successful_orders(request): #user can see orders whoose payment is done by him

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCompletedOrderHistory(request):   # User can see list of orders successfuly payed by him/her and completed as well.
    orders = PaytmOrder.objects.filter(user=request.user, is_completed=True)
    serialized_orders = PaytmOrderItemSerializer(orders, many=True)
    return Response(serialized_orders.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getInCompletedOrderHistory(request):   # User can see list of orders not payed by him/her.
    # print(request.META['HTTP_HOST'],"hahaha")
    orders = PaytmOrder.objects.filter(user=request.user, is_completed=False, isPaid=True)
    serialized_orders = PaytmOrderItemSerializer(orders, many=True)
    return Response(serialized_orders.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getVendorCompletedOrderHistory(request, rest_id):   # Vendor can see list of orders successfuly payed by users.
    orders = PaytmOrder.objects.filter(restaurant = rest_id, isPaid=True, is_completed=True)
    serialized_orders = PaytmOrderItemSerializer(orders, many=True)
    return Response(serialized_orders.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getVendorInCompletedOrderHistory(request, rest_id):   # Vendor can see list of orders not payed by users.
    orders = PaytmOrder.objects.filter(restaurant = rest_id, isPaid=True, is_completed=False)
    serialized_orders = PaytmOrderItemSerializer(orders, many=True)
    return Response(serialized_orders.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def markOutOfStock(request, item_id):
    item = MenuItems.objects.get(id = item_id)
    item.is_out_of_stock = not item.is_out_of_stock
    item.save()
    return Response({'success':True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOwnRestaurant(request):
    restaurant = Restaurant.objects.filter(admin=request.user).annotate(rating=Avg('review__rating'))
    serialized_restaurant = RestaurantSerializer(restaurant[0])
    # review_total = Review.objects.filter(restaurant=restaurant)
    return Response(serialized_restaurant.data)

@api_view(['GET'])
def getRestaurantById(request, id):
    restaurant = Restaurant.objects.filter(id=id).annotate(rating=Avg('review__rating'))
    serialized_restaurant = RestaurantSerializer(restaurant[0])
    return Response(serialized_restaurant.data)

@api_view(['GET'])
def getFAQ(request):
    faqs = FAQ.objects.all()
    serialized_faqs = FAQSerializer(faqs, many=True)
    return Response(serialized_faqs.data)

@api_view(['GET'])
def getCategories(request):
    fcategories = category.objects.all()
    serialized_categories = CategorySerializer(fcategories, many=True)
    return Response(serialized_categories.data)

@api_view(['GET'])
def getTax(request):
    tax = Tax.objects.all()[0]
    tax = tax.tax_percent
    return Response({"tax_percent":tax})