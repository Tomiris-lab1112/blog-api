
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import Count

from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import BooleanRadioFilter

from .models import User


# Form for creating a user
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


# Form for editing a user
class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text="Passwords are stored securely as hashes."
    )

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "user_info",
        "active_status",
        "staff_status",
        "post_count",
    )

    list_filter = (
        ("is_active", BooleanRadioFilter),
        ("is_staff", BooleanRadioFilter),
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    ordering = ("email",)
    list_per_page = 25

    readonly_fields = ("last_login",)

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password",
                ),
                "classes": ("tab",),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("tab",),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login",),
                "classes": ("tab",),
            },
        ),
    )

    add_fieldsets = (
        (
            "Create User",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _post_count=Count("posts", distinct=True)
        )

    @display(description="User", header=True)
    def user_info(self, obj):
        full_name = (
            f"{obj.first_name} {obj.last_name}".strip()
        )
        return full_name or obj.email, obj.email

    @display(
        description="Active",
        label={True: "success", False: "danger"},
    )
    def active_status(self, obj):
        return obj.is_active

    @display(
        description="Staff",
        label={True: "info", False: "warning"},
    )
    def staff_status(self, obj):
        return obj.is_staff

    @display(description="Posts", ordering="_post_count")
    def post_count(self, obj):
        return obj._post_count

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{count} users activated."
        )

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{count} users deactivated."
        )

    actions = (
        "activate_users",
        "deactivate_users",
    )


# Unfold admin for Groups
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    search_fields = ("name",)
    filter_horizontal = ("permissions",)
