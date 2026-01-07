from .models import User, AccessLevel, SystemAccessPermission
from . import serializers
from .permissions import IsStaffOrSuperuser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db.models import Q, Count
import random, openpyxl, jdatetime
from django.http import HttpResponse
from core.utils import apply_filters_and_sorting, get_accessible_queryset
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.MyTokenObtainPairSerializer
 

class LoginStepOneAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            otp = str(random.randint(100000, 999999))
            user.otp_code  = otp
            user.otp_code_created_at = timezone.now()
            user.save()

            send_mail(
                'کد ورود دو مرحله ای',
                f'کد تائید شما: {otp}',
                'aryanpuransanayeh@gmail.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'کد تایید به ایمیل شما ارسال شد.'}, status=200)
        
        return Response({'error': 'اطلاعات ورود اشتباه است.'}, status=401)


class LoginStepTwoAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        username = request.data.get('username')
        code = request.data.get('code')
        
        user = get_object_or_404(User, username=username)

        if user.otp_code == code:
            user.otp_code = None
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
        
        return Response({'error': 'کد تایید اشتباه است.'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserAPIView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        try:
           
            refresh_token = request.data["refresh_token"] 
            token = RefreshToken(refresh_token)
            
            token.blacklist() 

            return Response(
                {"detail": "با موفقیت از سیستم خارج شدید. توکن بی‌اعتبار شد."}, 
                status=status.HTTP_205_RESET_CONTENT 
            )
        
        except KeyError:
             return Response(
                {"error": "توکن رفرش (refresh_token) در درخواست یافت نشد."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "توکن رفرش نامعتبر است یا قبلاً بی‌اعتبار شده است."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "رمز عبور با موفقیت تغییر کرد. لطفا دوباره لاگین کنید."}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangeUserPasswordByAdminAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def patch(self, request, user_id):

        user = get_object_or_404(User, id=user_id)

        serializer = serializers.ChangeUserPasswordByAdmin(user, data=request.data)

        if serializer.is_valid():

            serializer.save()
            return Response({'message': f'رمز عبور {user.username} با موفقیت تغیر کرد'}, status=status.HTTP_200_OK)
        
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        serializer = serializers.UserProfileSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):

        user = request.user

        serializer = serializers.UserProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccessLevelAPIView(APIView):

    def get(self, request):

        access_levels = AccessLevel.objects.all()

        serializer = serializers.AccessLevelSerliazlizer(access_levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):

        serializer = serializers.AccessLevelSerliazlizer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, reqeust, access_id):
        
        access_level = get_object_or_404(AccessLevel, pk=access_id)
        
        access_level.delete()

        return Response({
            "message": f"{access_level.level_name} and thers subs are deleted"
        })
    
    def patch(self, request, access_id):
        
        access_level = get_object_or_404(AccessLevel, id=access_id)

        serializer = serializers.AccessLevelSerliazlizer(access_level, data=request.data, partial=True)
        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGroupAssignmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        serializer = serializers.GroupAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            target_groups = serializer.validated_data['group_ids']
            
            user.groups.set(target_groups)
            
            return Response({
                "detail": f"گروه‌های کاربر {user.username} آپدیت شدند."
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def post(self, request):

        serializer = serializers.UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = serializers.UserCreateSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, user_id):
        
        user = get_object_or_404(User, id=user_id)
        
        serializer = serializers.UserSerializer(user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, user_id):

        user = get_object_or_404(User, id=user_id)
        
        serializer = serializers.UserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        
        user = get_object_or_404(User, id=user_id)
        
        username = user.username
        user.delete()
        
        return Response(
            {"detail": f"کاربر '{username}' با موفقیت حذف شد."}, 
            status=status.HTTP_200_OK
        )
    

class UserSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request):

        accessibe_users = get_accessible_queryset(request, User, 'access_level')

        users_summary = accessibe_users.aggregate(
            total_count = Count('id'),
            active_count = Count('id', filter=Q(is_active=True)),
            diactive_count = Count('id', filter=Q(is_active=False)),
            admin_count = Count('id', filter=Q(is_staff=True)),
        )

        summary_data = [
            {'label': 'کل کاربران', 'count': users_summary['total_count']},
            {'label': 'کاربران فعال', 'count': users_summary['active_count']},
            {'label': 'کاربران غیرفعال', 'count': users_summary['diactive_count']},
            {'label': 'کاربران ادمین', 'count': users_summary['admin_count']},
        ]

        return Response(summary_data, status=status.HTTP_200_OK)
    

class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request):
        
        sorting_fields = ['created_at', '-created_at', 'name', '-name', 'username', '-username']
        applied_filters = ['access_level', 'groups', 'user_permissions', 'gender']
        searching_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
        users = apply_filters_and_sorting(request, sorting_fields, applied_filters, searching_fields, session_key='user', model=User)
        
        search_by = request.GET.get('q', '')
        if search_by:
            users = users.filter(
                Q(username__icontains=search_by) |
                Q(email__icontains=search_by) |
                Q(first_name__icontains=search_by) |
                Q(last_name__icontains=search_by) |
                Q(phone_number__icontains=search_by)
            )
        

        
        serializer = serializers.UserSerializer(users, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserPermissionAssignmentAPIView(APIView):
   
    permission_classes = [IsStaffOrSuperuser] 

    def patch(self, request, user_id): 
        
        user = get_object_or_404(User, id=user_id)
        

        serializer = serializers.UserPermissionAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_permissions = serializer.validated_data['permission_ids']
        
        user.user_permissions.set(target_permissions) 
        
        return Response(
            {"detail": f"مجوزهای خاص کاربر '{user.username}' با موفقیت به‌روزرسانی شد."}, 
            status=status.HTTP_200_OK
        )
    

class PermissionsListAPIView(APIView):
 
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request):
        
        ct = ContentType.objects.get_for_model(SystemAccessPermission)
        permissions_queryset = Permission.objects.filter(content_type=ct).values('id', 'name', 'codename').order_by('content_type', 'codename')
        
        permissions_serializer = serializers.PermissionDetailSerializer(permissions_queryset, many=True) 
        
        return Response(permissions_serializer.data, status=status.HTTP_200_OK)


class GroupsListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request):
        # Annotate each group with counts, using distinct=True to avoid inflated numbers caused by multiple JOINs.
        groups = Group.objects.annotate(
            users_count=Count('user', distinct=True),
            permissions_count=Count('permissions', distinct=True)
        )

        serializer = serializers.GroupSimpleSerializer(groups, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupsDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request, group_id):

        group = get_object_or_404(
            Group.objects.annotate(users_count=Count('user')),
            id=group_id
        )
        serializer = serializers.GroupsDetailSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):

        serializer = serializers.GroupsCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            group = serializer.save() 
            
            response_serializer = serializers.GroupsCreateSerializer(group)
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, group_id):

        group = get_object_or_404(Group, id=group_id)
        
        serializer = serializers.GroupsUpdateSerializer(group, data=request.data, partial=True)
        
        if serializer.is_valid():
        
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, group_id):

        group = get_object_or_404(Group, id=group_id)
        group.delete()
        return Response({'message': f'گروه {group.name} با موفقیت حذف شد'}, status=status.HTTP_200_OK)


class ExportUserAPIView(APIView):
    
    def get(self, request):

        sorted_by = request.session.get('user_sorted_by', 'created_at')
        filters = request.session.get('user_applied_filters', {})
        users = User.objects.all().filter(**filters).order_by(sorted_by)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.sheet_view.rightToLeft = True
        ws.title = 'کاربران'

        exclude_fields = ['password', 'otp_code', 'otp_created_at', 'date_joined']
        fields = [field for field in User._meta.fields if field.name not in exclude_fields]

        header = [str(field.verbose_name) for field in fields]
        header.append("گروه‌ها") 
        ws.append(header)
        
        for thing in users:
            row = []
            for field in fields:
                value = getattr(thing, field.name)

                if field.get_internal_type() == 'BooleanField':
                    value = "بله" if value else "خیر"
                
                elif field.name == 'access_level' and value:
                    value = value.level_name
                
                elif field.name == 'active_directory' and value:
                    value = value.username

                elif field.name in ['created_at', 'updated_at', 'last_login'] and value:
                    try:
                        value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')
                    except:
                        value = str(value)

                row.append(str(value) if value is not None else '-')
            
            user_groups = ", ".join([g.name for g in thing.groups.all()])
            row.append(user_groups if user_groups else '-')
            ws.append(row)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="users_export.xlsx"'
        wb.save(response)
        return response