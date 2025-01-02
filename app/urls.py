from django.urls import path
from .views import (HomePageView, BudgetListView, IncomeUpdateView,
                    ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('budget/', BudgetListView.as_view(), name='budget_list'),
    path('income/add/', IncomeUpdateView.as_view(), name='income_add'),
    path('expense/add/', ExpenseCreateView.as_view(), name='expense_add'),
    path('expense/<int:pk>/edit/', ExpenseUpdateView.as_view(), name='expense_edit'),
    path('expense/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense_delete'),
]
