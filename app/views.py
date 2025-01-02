from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Income, Expense, Budget, Category


class HomePageView(TemplateView):
    template_name = 'app/home.html'


class IncomeUpdateView(UpdateView):
    model = Income
    fields = ['amount']
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
    fields = ['name', 'amount', 'category']
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
        budget = Budget.objects.first()
        if not budget:
            budget = Budget.objects.create()
        context['budget'] = budget
        context['income'] = Income.objects.first()
        return context


class ExpenseUpdateView(UpdateView):
    model = Expense
    fields = ['name', 'amount', 'category']
    success_url = reverse_lazy('budget_list')


class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'app/expense_delete.html'
    success_url = reverse_lazy('budget_list')
