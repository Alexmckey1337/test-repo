from django.urls import path

from apps.lesson.api import views

urlpatterns = [
    path('lessons/text/', views.TextLessonListView.as_view(), name='lessons-text-list'),
    path('lessons/text/months/', views.TextLessonMonthListView.as_view(), name='lessons-text-months'),
    path('lessons/text/<str:slug>/', views.TextLessonDetailView.as_view(), name='lessons-text-detail'),
    path('lessons/text/<str:slug>/like/', views.TextLessonLikeView.as_view(), name='lessons-text-like'),
    path('lessons/text/<str:slug>/view/', views.TextLessonViewView.as_view(), name='lessons-text-view'),

    path('lessons/video/', views.VideoLessonListView.as_view(), name='lessons-video-list'),
    path('lessons/video/months/', views.VideoLessonMonthListView.as_view(), name='lessons-video-months'),
    path('lessons/video/<str:slug>/', views.VideoLessonDetailView.as_view(), name='lessons-video-detail'),
    path('lessons/video/<str:slug>/like/', views.VideoLessonLikeView.as_view(), name='lessons-video-like'),
    path('lessons/video/<str:slug>/view/', views.VideoLessonViewView.as_view(), name='lessons-video-view')
]
