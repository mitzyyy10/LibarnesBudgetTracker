from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    start_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.user.username

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Budget: ₱{self.amount} (Added: {self.date_added})"

    def save(self, *args, **kwargs):
        if self.__class__.objects.count() > 1 and self.pk is None:
            return
        super().save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date_spent = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.category}: ₱{self.amount:.2f} (Spent: {self.date_spent})"

class Budget(models.Model):
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_left = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_budget(self, start_date=None):
        if start_date:
            income_query = Income.objects.filter(date_added__gte=start_date)
            expense_query = Expense.objects.filter(date_spent__gte=start_date)
        else:
            income_query = Income.objects.all()
            expense_query = Expense.objects.all()
        self.total_income = income_query.aggregate(Sum('amount'))['amount__sum'] or 0
        self.total_expense = expense_query.aggregate(Sum('amount'))['amount__sum'] or 0
        self.budget_left = self.total_income - self.total_expense
        self.save()

    def __str__(self):
        return f"Budget Left: ₱{self.budget_left} (Since: {self.start_date})"

@receiver([post_save, post_delete], sender=Income)
@receiver([post_save, post_delete], sender=Expense)
def update_budget(sender, instance, **kwargs):
    budget, created = Budget.objects.get_or_create()
    budget.calculate_budget(budget.start_date)