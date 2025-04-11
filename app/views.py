from django.shortcuts import render
# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .serializer import *
from .models import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.http import JsonResponse

class BotUserViewset(ModelViewSet):
    queryset = BotUserModel.objects.all()
    serializer_class = BotUserSerializer
class GetUser(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('telegram_id',None):
            try:
                user = BotUserModel.objects.get(telegram_id=data['telegram_id'])
                serializer = BotUserSerializer(user, partial=True)
                return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
            except BotUserModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error':'Not found'},status=status.HTTP_204_NO_CONTENT)
class ChangeUserLanguage(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('telegram_id',None):
            try:
                user = BotUserModel.objects.get(telegram_id=data['telegram_id'])
                user.language = data['language']
                user.save()
                serializer = BotUserSerializer(user, partial=True)
                return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
            except BotUserModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error':'Not found'},status=status.HTTP_204_NO_CONTENT)
class TelegramChannelViewset(ModelViewSet):
    queryset = TelegramChannelModel.objects.all()
    serializer_class = TelegramChannelSerializer
class DeleteTelegramChannel(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('channel_id', None):
            try:
                user = TelegramChannelModel.objects.get(channel_id=data['channel_id'])
                user.delete()
                return Response({'status':"Deleted"},status=status.HTTP_200_OK)
            except TelegramChannelModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
class GetTelegramChannel(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('channel_id',None):
            try:
                channel = TelegramChannelModel.objects.get(channel_id=data['channel_id'])
                serializer = TelegramChannelSerializer(channel, partial=True)
                return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
            except TelegramChannelModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error':'Not found'},status=status.HTTP_204_NO_CONTENT)



class MeView(APIView):
    def get(self, request):
        telegram_id = request.session.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'Not authenticated'}, status=401)

        try:
            user = BotUserModel.objects.get(telegram_id=telegram_id)
            serializer = BotUserSerializer(user)
            return Response(serializer.data)
        except BotUserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        telegram_id = self.request.query_params.get('telegram_id')
        if not telegram_id:
            return Task.objects.none()
        try:
            user = BotUserModel.objects.get(telegram_id=telegram_id)
            return Task.objects.filter(user=user)
        except BotUserModel.DoesNotExist:
            return Task.objects.none()

    def perform_create(self, serializer):
        telegram_id = self.request.data.get('telegram_id')
        if telegram_id:
            try:
                user = BotUserModel.objects.get(telegram_id=telegram_id)
                serializer.save(user=user)
            except BotUserModel.DoesNotExist:
                raise serializers.ValidationError("User not found")

class TaskDetailView(APIView):
    def get(self, request, task_id):
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = BotUserModel.objects.get(telegram_id=telegram_id)
            task = Task.objects.get(id=task_id, user=user)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except BotUserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

class TaskStatusUpdateView(APIView):
    def patch(self, request, task_id):
        telegram_id = request.data.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = BotUserModel.objects.get(telegram_id=telegram_id)
            task = Task.objects.get(id=task_id, user=user)
            
            # Update status
            task.status = request.data.get('status', task.status)
            task.save()
            
            # Update user points and rank if task was completed
            if task.status:  # If status is True (completed)
                user.points += 2
                user.rank = user.points // 10
                user.save()
            
            return Response(TaskSerializer(task).data)
        except BotUserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

class UserRankView(APIView):
    def get(self, request):
        telegram_id = request.query_params.get('telegram_id')
        all_users = BotUserModel.objects.order_by('-points')

        ranked_users = []
        last_points = None
        current_rank = 0

        for idx, user in enumerate(all_users, start=1):
            if user.points != last_points:
                current_rank = idx
                last_points = user.points

            ranked_users.append({
                'telegram_id': user.telegram_id,
                'name': user.name,
                'points': user.points,
                'rank': current_rank,
                'streak':  0,
            })

        top_10_users = ranked_users[:10]

        # Handle requested user
        user_data = None
        if telegram_id:
            for user in ranked_users:
                if str(user['telegram_id']) == str(telegram_id):
                    user_data = user
                    break

        # Create response data
        response_data = {
            "top_users": top_10_users,
            "user": user_data
        }

        # Create JsonResponse and manually add CORS headers
        response = JsonResponse(response_data)
        response['Access-Control-Allow-Origin'] = 'https://9af3-95-214-210-137.ngrok-free.app'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        return response