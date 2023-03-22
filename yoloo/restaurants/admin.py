from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives


from restaurants.models import FAQ, PaytmOrder, Tax, User, Restaurant, MenuItems, Review, UserTransactionHistory, Order, College, RestaurantSpecificInfo, category

@admin.action(description='Mark selected restaurants as verified and send confirmation email')
def make_verified(modeladmin, request, queryset):
    # queryset.update(is_verified=True) #although restaurants should be actually verified but testing if we can implement this function
    # for future, a user would login as vendor and applying for reataurant by filling form, it might contain info like restaurant point on map(logitude, latitude)

    for data in queryset:
        data.is_verified = True
        data.save()
        # print(data.email)
        email = EmailMultiAlternatives(
            'Restaurant verification successfull',
            "<p>Congratulations!!! your retaurant is verified</p>",
            settings.EMAIL_HOST_USER,
            [data.email],
        )
        email.fail_silently = False
        email.send()
    # print(queryset.email)

@admin.action(description='create selected restaurants as verified and send confirmation email')
def verify_restaurant_admin(modeladmin, request, queryset): # this function would also create the restaurant instance for given restaurabt
    for data in queryset:
        new_restaurant =  Restaurant.objects.create(
            name = data.restaurant_name,
            addressString = data.addressString,
            tag_line = data.tag_line,
            media = data.media,
            admin_status = 1,
            shopkeeper_status = 0,#0 means on
            admin = data.owner,
            restaurant_email =data.restaurant_email,
            restaurant_phone =data.restaurant_phone,
        )

        new_restaurant.college.add(data.college)

        # data.owner.is_vendor = True
        owner = data.owner
        owner.is_vendor = True

        owner.save()

        email = EmailMultiAlternatives(
            'Restaurant verification successfull',
            "<p>Congratulations!!! your retaurant is verified</p>",
            settings.EMAIL_HOST_USER,
            [data.owner.email],
        )
        email.fail_silently = False
        email.send()
    # pass


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone', 'full_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'phone', 'full_name', 'is_active', 'is_admin')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    actions = [make_verified]

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('phone', 'full_name', 'is_admin', 'ver_code', 'is_vendor', 'is_verified', 'email', 'profile_picture')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('full_name','email','profile_picture')}),
        ('Permissions', {'fields': ('is_admin', 'is_verified', 'is_vendor', 'is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'password1', 'password2', 'email','profile_picture'),
        }),
    )
    search_fields = ('phone',)
    ordering = ('phone',)
    filter_horizontal = ()

class RestaurantSpecificInfoAdmin(admin.ModelAdmin):
    actions = [verify_restaurant_admin]

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
admin.site.register(Restaurant)
admin.site.register(MenuItems)
admin.site.register(Review)
admin.site.register(UserTransactionHistory)
admin.site.register(Order)
admin.site.register(College)
admin.site.register(PaytmOrder)
admin.site.register(RestaurantSpecificInfo, RestaurantSpecificInfoAdmin)
admin.site.register(FAQ)
admin.site.register(Tax)
admin.site.register(category)

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)