from django.db import models
# Create your models here.
class BotUserModel(models.Model):
    languages = (
        ('uz',"O'zbek",),
        ('en',"English")
    )
    name = models.CharField(max_length=300,null=True,blank=True,verbose_name="Full Name",help_text="Enter full name")
    telegram_id = models.CharField(max_length=100,unique=True,verbose_name="Telegram ID",help_text="Enter telegram id")
    language = models.CharField(max_length=5,default='uz',choices=languages,verbose_name="Language",help_text="Choose language")
    added = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)  # Reyting uchun

    groups = models.ManyToManyField(
        "auth.Group", related_name="custom_user_set", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_set", blank=True
    )
    def __str__(self):
        if self.name:
            return f"{self.name}"
        else:
            return f"User with ID:{self.telegram_id} "
    class Meta:
        verbose_name = 'Bot User'
        verbose_name_plural='Bot Users'
class TelegramChannelModel(models.Model):
    channel_id = models.CharField(max_length=150,verbose_name="Channel ID",help_text="Enter channel id",unique=True)
    channel_name = models.CharField(max_length=300,verbose_name="Channel Name",help_text="Enter channel name",null=True,blank=True)
    channel_members_count = models.CharField(max_length=200,null=True,blank=True,verbose_name="Channel Memers Count",help_text="Enter channel members count")
    def __str__(self):
        return f"Channel: {self.channel_id}"
    class Meta:
        verbose_name = 'Telegram Channel'
        verbose_name_plural = 'Telegram Channels'


from django.db import models


class Task(models.Model):
    user = models.ForeignKey(BotUserModel, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.BooleanField(default=False)  # False=incomplete, True=complete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TaskCompletion(models.Model):
    user = models.ForeignKey(BotUserModel, on_delete=models.CASCADE, related_name="task_completions")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completions")
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)


