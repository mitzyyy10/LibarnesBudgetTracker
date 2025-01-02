from django.contrib import admin
from .models import User, Income, Category, Expense, Budget

admin.site.register(User)
admin.site.register(Income)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Budget)
