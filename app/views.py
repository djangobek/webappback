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
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework import status as http_status

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
        # Get Telegram ID from headers
        telegram_id = request.headers.get('X-Telegram-ID')
        
        if not telegram_id:
            return Response(
                {'error': 'Telegram ID required in X-Telegram-ID header'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user = BotUserModel.objects.get(telegram_id=telegram_id)
            serializer = BotUserSerializer(user)
            return Response(serializer.data)
            
        except BotUserModel.DoesNotExist:
            return Response(
                {'error': 'User not found. Please register first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        


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
    




##########
################
##########
##########
##########
##########
@api_view(['GET'])
def check_user_by_telegram_id(request):
    telegram_id = request.query_params.get('telegram_id')

    if not telegram_id:
        return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
        serializer = BotUserSerializer(user)
        return Response({'exists': True, 'user': serializer.data}, status=status.HTTP_200_OK)
    except BotUserModel.DoesNotExist:
        return Response({'exists': False}, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_bot_user(request):
    serializer = BotUserCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        telegram_id = serializer.validated_data.get('telegram_id')

        # Check if user already exists
        if BotUserModel.objects.filter(telegram_id=telegram_id).exists():
            return Response({'error': 'User with this telegram_id already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({'message': 'User created successfully', 'user': serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def select_tasks(request):
    telegram_id = request.data.get('telegram_id')
    task_ids = request.data.get('task_ids', [])

    if not telegram_id or not isinstance(task_ids, list):
        return Response({'error': 'telegram_id and task_ids[] are required'}, status=status.HTTP_400_BAD_REQUEST)

    if len(task_ids) != 5:
        return Response({'error': 'You must select exactly 5 tasks'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
    except BotUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Prevent re-selection

    if UserTaskSelection.objects.filter(user=user).exists():
        return Response({'error': 'Tasks already selected'}, status=status.HTTP_400_BAD_REQUEST)

    tasks = ChallengeTask.objects.filter(id__in=task_ids)
    if tasks.count() != 5:
        return Response({'error': 'One or more invalid task IDs'}, status=status.HTTP_400_BAD_REQUEST)

    for task in tasks:
        UserTaskSelection.objects.create(user=user, task=task)
    if not user.challenge_start_date:
        user.challenge_start_date = timezone.now().date()
        user.save()

    return Response({'message': 'Tasks selected successfully'}, status=status.HTTP_201_CREATED)



def get_day_number(user):
    if not user.challenge_start_date:
        return None  # user hasn't started

    today = timezone.now().date()
    delta = (today - user.challenge_start_date).days + 1  # +1 to count from Day 1

    if delta > 30:
        return 30  # cap at 30
    elif delta < 1:
        return 1
    return delta

@api_view(['GET'])
def user_day_info(request):
    telegram_id = request.GET.get('telegram_id')

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
    except BotUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    day = get_day_number(user)

    return Response({
        'day_number': day,
        'total_points': user.points,
        'start_date': user.challenge_start_date
    })

@api_view(['POST'])
def complete_task(request):
    telegram_id = request.data.get('telegram_id')
    task_id = request.data.get('task_id')
    status_choice = request.data.get('status')  # 'done' or 'missed'

    if not telegram_id or not task_id or status_choice not in ['done', 'missed']:
        return Response({
            'error': 'telegram_id, task_id and valid status (done/missed) are required'
        }, status=http_status.HTTP_400_BAD_REQUEST)

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
    except BotUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)

    try:
        task = ChallengeTask.objects.get(id=task_id)
    except ChallengeTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=http_status.HTTP_404_NOT_FOUND)

    # Check if user selected this task
    if not UserTaskSelection.objects.filter(user=user, task=task).exists():
        return Response({'error': 'Task not part of user selection'}, status=http_status.HTTP_400_BAD_REQUEST)

    # Check if already logged today
    today = timezone.now().date()
    if DailyTaskLog.objects.filter(user=user, task=task, date=today).exists():
        return Response({'error': 'Already logged today'}, status=http_status.HTTP_400_BAD_REQUEST)

    # Create log with given status
    DailyTaskLog.objects.create(user=user, task=task, date=today, status=status_choice)

    # Add points if done
    if status_choice == "done":
        user.points += task.point
        user.save()

    return Response({'status': status_choice, 'message': 'Task logged successfully'}, status=http_status.HTTP_200_OK)

def refresh_user_ranks():
    users = BotUserModel.objects.all().order_by('-points', 'added')
    for index, user in enumerate(users, start=1):
        user.rank = index
        user.save()


@api_view(['GET'])
def top_challengers(request):
    top_users = BotUserModel.objects.order_by('-points', 'added')[:10]

    data = [
        {
            'name': user.name,
            'telegram_id': user.telegram_id,
            'points': user.points,
            'rank': user.rank,
        }
        for user in top_users
    ]
    return Response({'top_challengers': data})


@api_view(['GET'])
def get_user_selected_tasks(request):
    telegram_id = request.query_params.get('telegram_id')
    if not telegram_id:
        return Response({'error': 'telegram_id is required'}, status=400)

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
    except BotUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    today = timezone.now().date()
    selected_tasks = user.selected_tasks.select_related('task').all()

    data = []
    for sel in selected_tasks:
        # Check if this task has a log for today
        log = DailyTaskLog.objects.filter(user=user, task=sel.task, date=today).first()
        if log:
            status_value = log.status
        else:
            status_value = "unchanged"

        data.append({
            'id': sel.task.id,
            'title': sel.task.title,
            'description': sel.task.description,
            'time_start': sel.task.time_start,
            'time_end': sel.task.time_end,
            'point': sel.task.point,
            'status': status_value
        })

    return Response({'tasks': data})





@api_view(['GET'])
def get_all_challenge_tasks(request):

    tasks = ChallengeTask.objects.all()
    data = [
        {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'time_start': task.time_start,
            'time_end': task.time_end,
            'point': task.point,
        }
        for task in tasks
    ]
    return Response({'available_tasks': data})



@api_view(['GET'])
def get_user_challenge_progress(request):
    telegram_id = request.query_params.get('telegram_id')
    
    if not telegram_id:
        return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
    except BotUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if not user.challenge_start_date:
        return Response({'error': 'Challenge not started for this user'}, status=status.HTTP_400_BAD_REQUEST)

    today = timezone.now().date()
    start_date = user.challenge_start_date
    total_days = (today - start_date).days + 1  # include today

    selected_tasks = UserTaskSelection.objects.filter(user=user).select_related('task')
    task_ids = [st.task.id for st in selected_tasks]
    task_titles = {st.task.id: st.task.title for st in selected_tasks}

    data = {}

    for i in range(total_days):
        date = start_date + timedelta(days=i)
        logs = DailyTaskLog.objects.filter(user=user, date=date)
        log_dict = {log.task_id: log.status for log in logs}

        done = []
        missed = []

        for task_id in task_ids:
            status_value = log_dict.get(task_id, 'missed')  # default to 'missed'
            if status_value == 'done':
                done.append(task_titles[task_id])
            else:
                missed.append(task_titles[task_id])

        overall_status = "done" if len(done) >= len(missed) else "missed"

        data[f"day{i + 1}"] = {
            "date": date,
            "status": overall_status,
            "done": done,
            "missed": missed
        }

    return Response(data)

@api_view(['GET'])
def get_today_tasks_status(request):
    telegram_id = request.query_params.get('telegram_id')

    if not telegram_id:
        return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
    except BotUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    today = timezone.now().date()
    selected_tasks = UserTaskSelection.objects.filter(user=user).select_related('task')
    logs = DailyTaskLog.objects.filter(user=user, date=today)
    log_dict = {log.task_id: log.status for log in logs}

    tasks_with_status = []
    for selection in selected_tasks:
        task = selection.task
        status_str = log_dict.get(task.id, "missed")  # default to missed if no log
        tasks_with_status.append({
            "title": task.title,
            "status": status_str
        })

    return Response({
        "date": today,
        "tasks": tasks_with_status
    })

@api_view(['GET'])
def get_task_logs_by_user(request):
    telegram_id = request.query_params.get('telegram_id')
    task_id = request.query_params.get('task_id')

    if not telegram_id or not task_id:
        return Response({'error': 'telegram_id and task_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = BotUserModel.objects.get(telegram_id=telegram_id)
    except BotUserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        task = ChallengeTask.objects.get(id=task_id)
    except ChallengeTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    logs = DailyTaskLog.objects.filter(user=user, task=task).order_by('date')

    data = {
        str(log.date): log.status
        for log in logs
    }

    return Response(data, status=status.HTTP_200_OK)