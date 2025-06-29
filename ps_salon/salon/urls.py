from django.urls import path
from . import views

app_name = 'salon'
urlpatterns = [
    path('', views.index, name='index'),
    path('start/<int:table_id>/', views.start_session, name='start'),
    path('add/<int:table_id>/', views.add_item, name='add'),
    path('close/<int:table_id>/', views.close_session, name='close'),
    path('logs/', views.daily_log, name='daily_log'), 
]