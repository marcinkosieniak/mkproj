from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [path('base/', views.index, name = 'base'),
               path('', views.index, name = 'base'),
               path('proj-search/', views.proj_search, name = 'proj-search'),
               path('projekty/', views.projekty, name = 'projekty'),
               path('projekty/<int:pk>/', views.proj_detail, name = 'proj-detail'),
               path('projekty/<int:pk>/edit', views.proj_edit, name = 'proj_edit'),
               path('projekty/new/', views.proj_edit, name = 'proj_create'),
               path('projekty/<int:pk>/zyski', views.proj_zyski, name = 'proj_zyski'),
               path('projekty/<int:pk>/zyski/rooms', views.proj_rooms, name = 'proj_rooms'),
               path('projekty/<int:pk>/zyski/rooms/<int:rpk>', views.proj_rooms_ed, name = 'proj_rooms_edit'),
               path('projekty/<int:pk>/zyski/parts', views.proj_parts, name = 'proj_parts'),
               path('projekty/<int:pk>/zyski/parts/<int:rpk>', views.proj_parts_ed, name = 'proj_parts_ed'),
                ]
