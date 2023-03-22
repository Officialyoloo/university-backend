from django import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path('users/', views.getAllUsers),
    path('signup/', views.userSignUp),
    path('client-signup/',views.clientSignUp),
    path('vendor-signup/',views.vendorSignUp),
    # path('admin-signup/',views.adminSignUp),
    path('email-verify/<str:email>/<int:code>/',views.verifyEmail),
    path('client-login/',views.clientLogin),
    path('vendor-login/',views.vendorLogin),
    path('forgot-password/',views.forgotPasswordMailer),
    path('password-recovery/',views.forgotPasswordHandler),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # restaurant urls start
    path('restaurants/<int:college_id>', views.listRestaurants),
    path('rest-details/<int:id>/', views.restaurantDetails),

    path('reviews/<int:restId>/', views.showRatings),
    path('postratings/', views.sendRatings),

    path('client-details/', views.getClientDetails),
    path('user-reviews/', views.getReviewsByUser),

    path('update-user-profile/', views.updateClientProfile),
    path('update-restaurant-profile/', views.updateRestaurantProfile),

    path('pay/', views.start_payment, name="payment"),
    path('payment/success/', views.handle_payment_success, name="payment_success"),

    path('colleges/', views.getColleges),
    path('additem/', views.addFoodItems),
    path('getownitems/',views.getOwnRestaurantMenu),
    path('deleteitem/', views.deleteItem),

    # path('gethotels/', views.getHotelByCollege)
    # paytm payment integration starts
    path('paytm-pay/', views.paytm_start_payment, name="paytm_start_payment"),
    path('paytm-handlepayment/', views.paytm_handlepayment, name="paytm_handlepayment"),

    path('order-verifier/', views.orderVerifier),
    path('search/<int:college_id>/<str:search_term>/', views.searchByRestaurantAndMenu),
    path('restaurant-verify/', views.RestaurantVerifcationInfo),
    path('checkin-checkout/<int:rest_id>/', views.checkin_checkout),

    path('getmyorders/', views.getCompletedOrderHistory),
    path('getmyunorders/', views.getInCompletedOrderHistory),

    path('getvendororders/<int:rest_id>/', views.getVendorCompletedOrderHistory),
    path('getvendorunorders/<int:rest_id>/', views.getVendorInCompletedOrderHistory),

    path('myrestaurant/', views.getOwnRestaurant),

    path('outofstock/<int:item_id>', views.markOutOfStock),

    path('restaurantbyid/<int:id>/', views.getRestaurantById),

    path('faqs/', views.getFAQ),

    path('food-categories/', views.getCategories),

    path('gettax/', views.getTax)
]