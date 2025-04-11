from django.contrib import admin

# Register your models here.
from .models import BotUserModel,TelegramChannelModel
@admin.register(BotUserModel)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['name','telegram_id','language','points','rank','added']
    list_editable = ['language','name']
    list_display_links = ['telegram_id']
    list_per_page = 10
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