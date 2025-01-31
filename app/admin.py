from django.contrib import admin
from .models import UserProfile, Income, Category, Expense, Budget

admin.site.register(UserProfile)
admin.site.register(Income)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Budget)
