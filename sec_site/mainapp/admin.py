from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(ConfirmLogin)
admin.site.register(CustomSession)
admin.site.register(CustomPermission)
admin.site.register(CustomRole)
admin.site.register(Book)