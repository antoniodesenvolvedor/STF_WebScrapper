from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pesquisa', views.pesquisa, name='pesquisa'),
    path('aguardar_captura', views.aguardar_captura, name='aguardar_captura'),
    path('return_progress', views.return_progress, name='return_progress')
]