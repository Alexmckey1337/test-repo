from django.urls import path

from apps.lesson.api import views

urlpatterns = [
    path('lessons/text/', views.TextLessonListView.as_view()),
    path('lessons/text/months/', views.TextLessonMonthListView.as_view()),
    path('lessons/text/<str:slug>/', views.TextLessonDetailView.as_view()),
    path('lessons/video/', views.VideoLessonListView.as_view()),
    path('lessons/video/months/', views.VideoLessonMonthListView.as_view()),
    path('lessons/video/<str:slug>/', views.VideoLessonDetailView.as_view()),
]
