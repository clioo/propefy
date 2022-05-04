from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from apps.core import models


class ImagenesInmuebleInline(admin.TabularInline):
    model = models.Imagenes
    fields = ('photo',)


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


@admin.register(models.Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    inlines = [ImagenesInmuebleInline,]
    exclude = ['search_vector', 'point']

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Dueno)
admin.site.register(models.Categoria)
admin.site.register(models.Estado)
admin.site.register(models.Municipio)
admin.site.register(models.TipoPropiedad)
admin.site.register(models.PrecioPeriodo)
