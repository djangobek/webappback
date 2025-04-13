from django.contrib import admin

# Register your models here.
from .models import *

@admin.register(TelegramChannelModel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ['channel_id','channel_name','channel_members_count']
    list_display_links = ['channel_name']
    list_per_page = 10


from django.contrib import admin
from .models import BotUserModel, Task, TaskCompletion



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "start_time", "end_time")

@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "date", "completed")


class UserTaskSelectionInline(admin.TabularInline):
    model = UserTaskSelection
    extra = 0
    readonly_fields = ('task', 'created_at')
    can_delete = False


# ---------------------
# Inline for viewing daily task logs in user admin
class DailyTaskLogInline(admin.TabularInline):
    model = DailyTaskLog
    extra = 0
    readonly_fields = ('task', 'date', 'status')
    can_delete = False


# ---------------------
@admin.register(BotUserModel)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'telegram_id', 'language', 'points', 'rank', 'added')
    list_filter = ('language', 'added')
    search_fields = ('name', 'telegram_id')
    readonly_fields = ('points', 'rank', 'added')
    inlines = [UserTaskSelectionInline, DailyTaskLogInline]


# ---------------------
@admin.register(ChallengeTask)
class ChallengeTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'point', 'time_start', 'time_end')
    search_fields = ('title',)
    list_filter = ('point',)


# ---------------------
@admin.register(UserTaskSelection)
class UserTaskSelectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'task', 'created_at')
    search_fields = ('user__name', 'user__telegram_id', 'task__title')
    list_filter = ('created_at',)


# ---------------------
@admin.register(DailyTaskLog)
class DailyTaskLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'task', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__name', 'user__telegram_id', 'task__title')
    date_hierarchy = 'date'


# ---------------------
@admin.register(MotivationMessage)
class MotivationMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_text', 'created_at')
    search_fields = ('text',)
    readonly_fields = ('created_at',)

    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Message'