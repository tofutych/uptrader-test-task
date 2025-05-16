from django import forms
from django.contrib import admin

from .models import MenuItem


class MenuItemModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        prefix = "--- " * obj.get_indent()
        return f"{prefix}{obj.name} (ID: {obj.id})"


class MenuItemAdminForm(forms.ModelForm):
    parent = MenuItemModelChoiceField(
        queryset=MenuItem.objects.all(),
        required=False,
        label="Родительский пункт",
    )

    class Meta:
        model = MenuItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance and instance.pk:
            self.fields["parent"].queryset = MenuItem.objects.exclude(pk=instance.pk)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemAdminForm
    list_display = (
        "name",
        "menu_name",
        "parent",
        "get_url_display",
        "order",
        "explicit_url",
        "named_url",
    )
    list_filter = ("menu_name", "parent")
    search_fields = ("name", "menu_name")
    ordering = ("menu_name", "parent__id", "order", "name")

    def get_url_display(self, obj):
        return obj.get_url()

    get_url_display.short_description = "Разрешенный URL"
