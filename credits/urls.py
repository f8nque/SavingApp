from django.urls import path
from . import views
urlpatterns = [
    path('debtregistration/',views.DebtRegistrationView.as_view(),name='debt_registration'),
    path('debtservice/',views.DebtServiceView.as_view(),name='debt_service'),
    path('debtlist/',views.DebtSummaryView.as_view(),name='debt_list'),
    path('debthistory/<int:pk>/',views.DebtServiceHistoryView.as_view(),name='debt_history'),
    path('updatedebtregistration/<int:pk>/',views.UpdateDebtRegistrationView.as_view(),name='update_debt_registration'),
    path('updatedebtservice/<int:pk>/',views.UpdateDebtServiceView.as_view(),name='update_debt_service'),
    path('deletedebtregistration/<int:pk>/',views.DeleteDebtRegistrationView.as_view(),name='delete_debt_registration'),
    path('deletedebtservice/<int:pk>/',views.DeleteDebtServiceView.as_view(),name='delete_debt_service'),
    ]