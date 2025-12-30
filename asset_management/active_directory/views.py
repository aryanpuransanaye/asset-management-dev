from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ActiveDirectory
from accounts.models import User
from . import serializers
import ldap3


class ActiveDirectoryListAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):

        activate_directories = ActiveDirectory.objects.all()
        serializer = serializers.ActiveDirectorySerializer(activate_directories, many = True)

        return Response(serializer.data)
    

class ActiveDirectoryAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, active_directory_id):

        active_directory = get_object_or_404(ActiveDirectory, id = active_directory_id)
        serializer = serializers.ActiveDirectorySerializer(active_directory)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        
        serializer = serializers.ActiveDirectorySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, active_directory_id):

        active_directory = get_object_or_404(ActiveDirectory, id = active_directory_id)
        serializer = serializers.ActiveDirectorySerializer(active_directory, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        # accessible_queryset = get_accessible_queryset(request, model=Hardware)
        active_directories = ActiveDirectory.objects.filter(id__in = ids_to_delete)

        if not active_directories.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = active_directories.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)


class ActiveDirectoryTestConnectionAPIView(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, active_directory_id=None):
      
        if active_directory_id:
            config = get_object_or_404(ActiveDirectory, id=active_directory_id)
            server_address = config.server_address
            port = config.port
            user_dn = f"{config.username}@{config.domain_name}"
            password = config.password
     
        else:
            server_address = request.data.get('server_address')
            port = request.data.get('port', 389)
            user_dn = f"{request.data.get('username')}@{request.data.get('domain_name')}"
            password = request.data.get('password')

        try:
            server = ldap3.Server(server_address, port=int(port), connect_timeout=5)
            
            conn = ldap3.Connection(
                server, 
                user=user_dn, 
                password=password, 
                auto_bind=True
            )

            return Response({
                "message": "اتصال با موفقیت برقرار شد. نام کاربری و رمز عبور صحیح است.",
                "status": "success"
            }, status=status.HTTP_200_OK)

        except ldap3.core.exceptions.LDAPBindError:
            return Response({
                "errors": "خطا در احراز هویت: نام کاربری یا رمز عبور اشتباه است.",
                "status": "auth_error"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except ldap3.core.exceptions.LDAPNetworkError:
            return Response({
                "errors": "خطا در شبکه: سرور در دسترس نیست یا پورت بسته است.",
                "status": "network_error"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "errors": f"خطای نامشخص: {str(e)}",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)


class ActiveDirectoryScannerAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, active_directory_id):

        config = get_object_or_404(ActiveDirectory, id=active_directory_id)
        new_users_data = [] 

        try:
          
            server = ldap3.Server(config.server_address, port=config.port)
            conn = ldap3.Connection(server, user=f"{config.username}@{config.domain_name}", 
                                    password=config.password, auto_bind=True)
            
            conn.search(search_base=config.search_base, 
                        search_filter='(&(objectClass=user)(objectCategory=person))', 
                        attributes=['sAMAccountName', 'mail', 'givenName', 'sn'])

            for entry in conn.entries:
                user_data = {
                    'username': entry.sAMAccountName.value,
                    'email': entry.mail.value if entry.mail else f"{entry.sAMAccountName.value}@local.com",
                    'first_name': entry.givenName.value if entry.givenName else "",
                    'last_name': entry.sn.value if entry.sn else "",
                    'active_directory_server': config.id
                }
                new_users_data.append(user_data)

            serializer = serializers.CreateScannedADUserSerializer(data=new_users_data, many=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": f"تعداد {len(serializer.data)} کاربر با موفقیت وارد شدند.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)