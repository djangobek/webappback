from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter()
router.register('botuser',BotUserViewset)
router.register('channels',TelegramChannelViewset)
urlpatterns = [
    path('',include(router.urls)),
    path('user/',GetUser.as_view()),
    path('lang/',ChangeUserLanguage.as_view()),
    path('channel/',GetTelegramChannel.as_view()),
    path('delete_channel/',DeleteTelegramChannel.as_view()),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:task_id>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/status/', TaskStatusUpdateView.as_view(), name='task-status-update'),
    path('rankings/', UserRankView.as_view(), name='user-rankings'),
    path('profile/', get_user_profile_info, name='user-profile'),
    path('check-user/', check_user_by_telegram_id, name='check-user'),
    path('create-user/', create_bot_user, name='create-bot-user'),
    path('select-tasks/', select_tasks),
    path('complete-task/', complete_task),
    path('user-day-info/', user_day_info, name='user-day-info'),
    path('top-challengers/', top_challengers, name='top-challengers'),
    path('user-tasks/', get_user_selected_tasks, name='get-user-tasks'),
    path('all-tasks/', get_all_challenge_tasks, name='get-all-tasks'),
    path("user-progress/", get_user_challenge_progress, name="user-progress"),
    path('today-task-status/', get_today_tasks_status, name='today-task-status'),
    path('calendar/', get_task_logs_by_user, name='calendar'),
    path("scheduled-tasks/", ScheduledTasksAPIView.as_view()),

]
