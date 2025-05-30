from django.urls import path
from . import views

urlpatterns = [
    path('sell/', views.sell_product, name='sell'),
    path('monitoring/', views.monitoring, name='monitoring'),
]
