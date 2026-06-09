from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import UserProfile


admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    can_delete = False
    show_change_link = False
    verbose_name = 'Профиль'
    verbose_name_plural = 'Кодовая фраза'

    def get_fields(self, request, obj=None):
        return ['passphrase']

    def has_view_permission(self, request, obj=None):
        return obj is not None and obj.pk == request.user.pk

    def has_change_permission(self, request, obj=None):
        return obj is not None and obj.pk == request.user.pk

    def has_add_permission(self, request, obj=None):
        return obj is not None and obj.pk == request.user.pk


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = ['username', 'first_name', 'last_name', 'email', 'get_role', 'is_active']
    list_display_links = ['username']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ['is_active', 'groups']

    def get_role(self, obj):
        if obj.groups.filter(name='admin').exists():
            return 'Администратор'
        if obj.groups.filter(name='teacher').exists():
            return 'Преподаватель'
        return '—'
    get_role.short_description = 'Роль'

    admin_fieldsets = (
        ('Учётные данные', {'fields': ('username', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'email')}),
        ('Роль и доступ', {'fields': ('is_active', 'groups')}),
        ('Даты', {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )

    admin_teacher_fieldsets = (
        ('Учётные данные', {'fields': ('username',)}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'email')}),
        ('Роль и доступ', {'fields': ('is_active', 'groups')}),
        ('Даты', {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )

    teacher_fieldsets = (
        ('Учётные данные', {'fields': ('username', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'email')}),
    )

    add_fieldsets = (
        ('Учётные данные', {'fields': ('username', 'password1', 'password2')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'email')}),
        ('Роль', {'fields': ('groups',)}),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        if request.user.groups.filter(name='teacher').exists():
            return self.teacher_fieldsets
        if obj.groups.filter(name='teacher').exists():
            return self.admin_teacher_fieldsets
        return self.admin_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in ['user_permissions', 'is_staff', 'is_superuser']:
            if field in form.base_fields:
                del form.base_fields[field]
        if 'password' in form.base_fields:
            form.base_fields['password'].help_text = (
                'Пароли в открытом виде не хранятся. '
                'Для смены пароля используйте кнопку ниже.'
            )
        return form

    def get_inline_instances(self, request, obj=None):
        if obj and obj.pk == request.user.pk:
            UserProfile.objects.get_or_create(user=obj)
            return [UserProfileInline(self.model, self.admin_site)]
        return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='teacher').exists():
            return qs.filter(pk=request.user.pk)
        return qs

    def changelist_view(self, request, extra_context=None):
        if request.user.groups.filter(name='teacher').exists():
            return HttpResponseRedirect(
                reverse('admin:auth_user_change', args=[request.user.pk])
            )
        return super().changelist_view(request, extra_context)

    def has_view_permission(self, request, obj=None):
        if request.user.groups.filter(name='teacher').exists():
            if obj is None:
                return True
            return obj == request.user
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='admin').exists():
            return True
        if request.user.groups.filter(name='teacher').exists():
            if obj is None:
                return True
            return obj == request.user
        return False

    def has_add_permission(self, request):
        return request.user.groups.filter(name='admin').exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_perms(self, app_label):
        return True

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance

        if not obj.is_staff:
            obj.is_staff = True
            obj.save()

        if obj.groups.filter(name='teacher').exists():
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.auth.models import Permission
            ct = ContentType.objects.get_for_model(User)
            view_perm = Permission.objects.get(content_type=ct, codename='view_user')
            change_perm = Permission.objects.get(content_type=ct, codename='change_user')
            obj.user_permissions.add(view_perm, change_perm)
            UserProfile.objects.get_or_create(user=obj)

    filter_horizontal = ['groups']


admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ['name']

    def has_add_permission(self, request):
        return request.user.groups.filter(name='admin').exists()

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='admin').exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = 'Система контроля знаний'
admin.site.site_title = 'Администрирование'
admin.site.index_title = 'Управление пользователями'