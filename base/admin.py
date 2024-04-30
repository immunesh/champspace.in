from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Course)
admin.site.register(CustomUser)
admin.site.register(GammaUser)
admin.site.register(BetaUser)
admin.site.register(isPurchased)