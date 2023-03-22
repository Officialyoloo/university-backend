from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.core.validators import RegexValidator


class MyUserManager(BaseUserManager):
    def create_user(self, phone, full_name, email=None, password=None, ver_code = None, is_vendor=False):
        """
        Creates and saves a User with the given phone, email, name and password.
        """
        if not phone:
            raise ValueError('Users must have a phone number')

        user = self.model(
            phone = phone,
            full_name=full_name,
            email = email,
            ver_code = ver_code,
            is_vendor=is_vendor
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, full_name, email=None, password=None, ver_code = None, is_vendor=False):
        """
        Creates and saves a superuser with the given phone, full_name and password.
        """
        user = self.create_user(
            phone,
            password=password,
            full_name=full_name,
            email = email,
            ver_code = ver_code,
            is_vendor=is_vendor
        )
        user.is_admin = True
        user.is_verified = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    phone_regex = RegexValidator(regex=r'^[6-9]\d{9}$', message="Phone number must be entered in the format: '999999999'. Exact 10 digits allowed.")
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    phone = models.CharField(validators=[phone_regex], max_length=25, unique=True)
    full_name = models.CharField(max_length=40)
    ver_code = models.IntegerField(default=0, null=True, blank=True)
    ver_code_update_time = models.DateTimeField(auto_now=True) #time at the time of update, we can take 10 min difference for validity
    is_active = models.BooleanField(default=True) # has user's mail verified
    is_admin = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False) #is vendor verified by admin
    # profile_pic = models.FileField(upload_to="dishes/", blank=True, null=True)
    profile_picture = models.FileField(upload_to="dishes/", blank=True, null=True)
    referral_code = models.CharField(max_length=10)
    reward_points = models.IntegerField(default=0)
    reference_code = models.CharField(max_length=20, null = True, blank=True) #it is referral code of user who referred us.

    objects = MyUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

# Create your models here.
class College(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class Restaurant(models.Model):
    AdminStatus = (
        (0, "Not Approved"),
        (1, "Approved"),
        (2, "Blocked"),
        (3, "Temporarily closed")
    )
    ShopkeeperStatus = (
        (0, "Available"),
        (1, "Closed")
    )
    name = models.CharField(max_length=50)
    addressOnMap = models.CharField(max_length=200, null = True, blank=True)
    addressString = models.CharField(max_length=200)
    average_rating = models.DecimalField(default = 0.0, max_digits=4, decimal_places=2)
    tag_line = models.CharField(max_length=255)
    media = models.FileField(upload_to="restaurant/")
    admin_status = models.IntegerField(choices=AdminStatus)
    shopkeeper_status = models.IntegerField(choices=ShopkeeperStatus) #It would be kind of checkin-checkout that would be done by shopkeeper every day
    admin = models.ForeignKey(User, on_delete=models.CASCADE) # ye malik h
    college = models.ManyToManyField(College)
    # new fields
    restaurant_email = models.EmailField(max_length=50)
    phone_regex = RegexValidator(regex=r'^[6-9]\d{9}$', message="Phone number must be entered in the format: '999999999'. Exact 10 digits allowed.")
    restaurant_phone = models.CharField(validators=[phone_regex], max_length=25)

    def __str__(self):
        return self.name

class RestaurantSpecificInfo(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^[6-9]\d{9}$', message="Phone number must be entered in the format: '999999999'. Exact 10 digits allowed.")
    restaurant_phone = models.CharField(validators=[phone_regex], max_length=25)
    restaurant_email = models.EmailField(max_length=50)
    owner_phone = models.CharField(max_length=15)
    adhar_card = models.FileField(upload_to="restaurant-credentials/")
    restaurant_name = models.CharField(max_length=50)
    # owner_name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pan_card = models.FileField(upload_to="restaurant-credentials/")
    FSSAI_certificate = models.FileField(upload_to="restaurant-credentials/")
    addressString = models.CharField(max_length=200)
    tag_line = models.CharField(max_length=255)
    media = models.FileField(upload_to="restaurant/")

class MenuItems(models.Model):
    # CATEGORY = (
    #     (0,"Thali"),
    #     (1,"Vegies"),
    #     (2,"Beverages"),
    #     (3, "Breads")
    # )

    is_veg = models.BooleanField(default=1) # 1->Yes, 0->No
    dish_name = models.CharField(max_length=50)
    serving = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # average_rating = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    dish_picture = models.FileField(upload_to="dishes/")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    explainer_line = models.CharField(max_length=50, null=True, blank=True)    #can be helpful when we want to show what exactly is a particular dish
    show_explainer_line = models.BooleanField(default=False) #0 -> no, 1-> Yes
    is_out_of_stock = models.BooleanField(default=False) #0 -> no, 1-> Yes
    food_category = models.IntegerField()

    def __str__(self):
        return self.dish_name

class Review(models.Model):
    rating = models.DecimalField(default = 0.0, max_digits=4, decimal_places=1)
    item_name = models.CharField(max_length=50) #to mention above comments
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.item_name

# below models are open for changes
class UserTransactionHistory(models.Model):
    item_id = models.ForeignKey(MenuItems, on_delete=models.CASCADE) #menu item id
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    quantity = models.IntegerField()

# for test
class Order(models.Model):
    order_product = models.CharField(max_length=100)
    order_amount = models.CharField(max_length=25)
    order_payment_id = models.CharField(max_length=100)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)
    Orderer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order_mode = models.BooleanField(default=0) #0->Dine out, 1-> pickup

    def __str__(self):
        return self.order_product

class OrderDetails(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)


# paytm-gateway starts
class PaytmOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # product_name = models.CharField(max_length=100)
    order_amount = models.DecimalField(max_digits=6, decimal_places=2)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order_schedule_date = models.DateTimeField() # for experiment it is auto now
    otp = models.IntegerField(default=0) #4 digit otp to be verified at the time of takeaway from restaurant
    is_completed = models.BooleanField(default=False) #tells weather end user have collected the food.
    order_mode = models.BooleanField() # 0-> Dine out, 1 -> Pick up

    # def __str__(self):
    #     return self.product_name

class PaytmOrderDetails(models.Model):
    # item_id = models.IntegerField()
    item_name = models.CharField(max_length=100)
    item_price = models.DecimalField(max_digits=6, decimal_places=2)
    item_serving = models.IntegerField()
    order = models.ForeignKey(PaytmOrder, related_name='order_details', on_delete=models.CASCADE)

class FAQ(models.Model):
    question = models.CharField(max_length = 500)
    answer = models.CharField(max_length=1000)

class Tax(models.Model):
    tax_percent = models.DecimalField(max_digits=4, decimal_places=2)

class category(models.Model):
    name = models.CharField(max_length=50)