from rest_framework.serializers import ModelSerializer
from .models import BotUserModel,TelegramChannelModel
class BotUserSerializer(ModelSerializer):
    class Meta:
        model = BotUserModel
        fields = '__all__'
class TelegramChannelSerializer(ModelSerializer):
    class Meta:
        model = TelegramChannelModel
        fields = '__all__'


from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, TaskCompletion
from rest_framework import serializers
from .models import BotUserModel, Task, TaskCompletion


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "telegram_id", "points", "rank")

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCompletion
        fields = "__all__"

