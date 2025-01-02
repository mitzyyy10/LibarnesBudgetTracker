from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.user.username

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Budget: ₱{self.amount}"

    def save(self, *args, **kwargs):
        if self.__class__.objects.count() > 1 and self.pk is None:
           return
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Expense(models.Model):
    name = models.CharField(max_length=100, default="Miscellaneous")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category,on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.category}: ₱{self.amount:.2f}"


class Budget(models.Model):
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_left = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_budget(self):
        self.total_income = Income.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        self.total_expense = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        self.budget_left = self.total_income - self.total_expense
        self.save()

    def __str__(self):
        return f"Budget Left: ₱{self.budget_left}"


@receiver([post_save, post_delete], sender=Income)
@receiver([post_save, post_delete], sender=Expense)
def update_budget(sender, instance, **kwargs):
    budget, created = Budget.objects.get_or_create()
    budget.calculate_budget()