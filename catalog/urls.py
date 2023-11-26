from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('home', views.landing_page, name='landing_page'),
    path('', views.loader, name='loader'),
    path('shop',views.shop, name='shop' ),
    path('checkout/', views.checkout, name='checkout'),
    path('success', views.success, name='success'),
    path('unsuccess', views.unsuccess, name='unsuccess'),
    path('<path:undefined_path>',views.error, name='error'),
]
