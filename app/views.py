from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Income, Expense, Budget, Category, UserProfile
from django.utils import timezone
from django.db.models import Sum
from django import forms


class IncomeForm(forms.ModelForm):
    date_added = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        initial=timezone.now
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount'
        })
    )

    class Meta:
        model = Income
        fields = ['amount', 'date_added']

class ExpenseForm(forms.ModelForm):
    date_spent = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        initial=timezone.now
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter expense name'
        })
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = Expense
        fields = ['name', 'amount', 'category', 'date_spent']
class HomePageView(TemplateView):
    template_name = 'app/home.html'


class IncomeUpdateView(UpdateView):
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('budget_list')

    def get_object(self, queryset=None):
        income, created = Income.objects.get_or_create()
        return income

    def form_valid(self, form):
        response = super().form_valid(form)
        Budget.objects.first().calculate_budget()
        return response


class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy('budget_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        Budget.objects.first().calculate_budget()
        return response


class BudgetListView(ListView):
    model = Expense
    template_name = 'app/budget_list.html'
    context_object_name = 'expenses'

    def get_context_data(self, **_):
        context = super().get_context_data()

        start_date = self.request.GET.get('start_date')

        budget = Budget.objects.first()
        if not budget:
            budget = Budget.objects.create()

        if start_date:
            expenses = Expense.objects.filter(date_spent=start_date).order_by('-date_spent')

            income = Income.objects.filter(date_added=start_date).aggregate(Sum('amount'))['amount__sum'] or 0
            expense_total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

            budget.total_income = income
            budget.total_expense = expense_total
            budget.budget_left = income - expense_total
            budget.save()

            context['expenses'] = expenses
            context['selected_date'] = start_date
        else:

            budget.calculate_budget()
            context['expenses'] = Expense.objects.all().order_by('-date_spent')

        context['budget'] = budget
        context['income'] = Income.objects.first()

        return context


class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy('budget_list')


class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'app/expense_delete.html'
    success_url = reverse_lazy('budget_list')


