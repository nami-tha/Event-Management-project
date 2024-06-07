from rest_framework import generics
from .models import  User,Event
from .serializers import EventSerializer,Registration
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView
from .serializers import UserSerializer,EventSerializer,RegistrationSerializer,LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

class UserCreateView(generics.CreateAPIView):
    """ User  Create View """
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Add custom response message
        response.data['message'] = "User created successfully"
        return response  
    

class UserListView(ListAPIView):
    """ User List View"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "admin": 
            return User.objects.all()
        else:
            raise PermissionDenied("You don't have permission to access this resource.")
    
 
class UserDetailView(RetrieveUpdateDestroyAPIView):
    """ User Detail View """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return User.objects.all()


    def get_object(self):
        obj = super().get_object()
        # Check if the requesting user is the owner of the object
        if obj != self.request.user:
            raise PermissionDenied("You don't have permission to perform this action.")
        return obj 
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Add custom response message
        response.data['message'] = "User updated successfully"
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = "User {} has been deleted successfully.".format(instance.username)
        return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)
 
class EventListView(ListCreateAPIView):
    """ Event Create View and List View """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    
    
    def get_queryset(self):
        user = self.request.user
        print(user)
        # Check user role and return appropriate queryset
        if user.role == 'organizer':
            return Event.objects.filter(organizer=user)
        queryset = Event.objects.all()
        return queryset
        
    
    def perform_create(self, serializer):
        user = self.request.user
        # Check user role and return appropriate queryset
        if user.role == 'organizer':
            serializer.save()
        else:
            raise PermissionDenied("You don't have permission to perform this action.")
            

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Add custom response message
        response.data['message'] = "Event created successfully"
        return response

    
class EventDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    
    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)
    
    def get_object(self):
        queryset = self.get_queryset()
        # Get the event object based on the provided lookup field
        obj = queryset.filter(id=self.kwargs['id']).first()
        if obj is None:
            # If the event doesn't exist or the user is not the organizer, raise PermissionDenied
            raise PermissionDenied("You don't have permission to perform this action.")
        return obj
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Add custom response message
        response.data['message'] = "Event updated successfully"
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = "Event {} has been deleted successfully.".format(instance.title)
        return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)
    
    
    
class RegistrationCreateView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        event_id = self.request.data.get('event')
        if not event_id:
            raise ValidationError({'event': 'This field is required.'})

        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError({'event': 'Event not found.'})

        user = self.request.user
        if user.role != "attendee":
            raise PermissionDenied("Only attendee users can register events.")
        
        serializer.save(user=user, event=event)
         
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Add custom response message
        response.data['message'] = "Event Register successfully"
        return response
    
class EventRegistrationCountView(APIView):
    def get(self, request):
        # Count the number of events and registrations
        event_count = Event.objects.count()
        registration_count = Registration.objects.count()
        return Response({
            'event_count': event_count,
            'registration_count': registration_count
        })
            
        
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    def post(self, request):
        refresh_token = self.request.data.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
            except Exception as e:
                return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)