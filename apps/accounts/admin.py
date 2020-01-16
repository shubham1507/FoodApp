from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from .models import EmailUser


class EmailUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    def __init__(self, *args, **kargs):
        super(EmailUserCreationForm, self).__init__(*args, **kargs)

    class Meta:
        model = EmailUser
        fields = '__all__'


class EmailUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    def __init__(self, *args, **kargs):
        super(EmailUserChangeForm, self).__init__(*args, **kargs)

    class Meta:
        model = EmailUser
        fields = '__all__'


class UserTypeListFilter(admin.SimpleListFilter):
    title = _('User Type')

    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('seller', _('Seller')),
            ('buyer', _('Buyer')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'seller':
            return queryset.filter(is_seller=True)
        if self.value() == 'buyer':
            return queryset.filter(is_buyer=True)


class EmailUserAdmin(UserAdmin):
    """
    The following attributes may need to be overridden if your User's
    fields don't match up with the built-in User:
    form
    add_form
    change_password_form
    list_display
    list_filter
    fieldsets
    add_fieldsets
    search_fields
    ordering
    filter_horizontal
    """

    form = EmailUserChangeForm
    add_form = EmailUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_superuser',
                    'is_seller', 'is_buyer', 'is_seller_approved')

    list_filter = (UserTypeListFilter, )

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': (
                'first_name',
                'last_name',
                'image',
                'phone_number',
            )
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


    # admin.site.register(EmailUser, EmailUserAdmin)

