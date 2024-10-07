from django.urls import path
from myapp import views
urlpatterns = [
    path('', views.index),
    path('create/', views.create),
    path('read/<id>/', views.read),
    path('delete/', views.delete),
    path('update/<id>/', views.update),

    path('api/posts/', PostListCreateAPIView.as_view()),  # 전체 조회 및 생성
    path('api/posts/<int:id>/', PostDetailAPIView.as_view()),
]
