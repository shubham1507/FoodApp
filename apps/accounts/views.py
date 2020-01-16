from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken as OriginalObtain
from .models import EmailUser
from .serializers import EmailUserSerializer, AuthTokenSerializer, CreateEmailUserSerializer
from .permissions import BaseUserPermission

# Create your views here.

EMAILUSER_VALUES = [
    'id',
    'first_name',
    'last_name',
    'email',
    'city',
    'company_name',
    'company_logo',
    'is_seller',
    'is_buyer',
    'is_superuser',
]


class GenericErrorResponse(Response):
    def __init__(self, message):
        # Ensure that the message always gets to the user in a standard format.
        if isinstance(message, ValidationError):
            message = message.detail
        if isinstance(message, str):
            message = [message]
        super().__init__({"non_field_errors": message}, status=400)


class ObtainAuthToken(OriginalObtain):
    def post(self, request, require_validated=True):
        serializer_class = AuthTokenSerializer
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.validated_data['user']
        except Exception as e:
            return Response(data={'errorMessage': serializer.validated_data},
                            status=200)
        token, created = Token.objects.get_or_create(user=user)
        # notification_user = FCMDevice.objects.filter(user_id=user.id).update(
        #     active=False)
        # crate_notification_user = FCMDevice.objects.create(
        #     registration_id=self.request.data['registration_id'],
        #     user_id=user.id,
        #     type=self.request.data['type'])

        return Response({
            'result': 'success',
            'email': user.email,
            'is_seller': user.is_seller,
            'is_buyer': user.is_buyer,
            'token': token.key,
            'id': user.id
        })


obtain_auth_token = ObtainAuthToken.as_view()


class EmailUserViewSet(viewsets.ModelViewSet):

    serializer_class = EmailUserSerializer
    permission_classes = (IsAuthenticated, )
    queryset = EmailUser.objects.all()

    def get_queryset(self):
        q = self.queryset

        if 'email' in self.request.query_params:
            return q.filter(email=self.request.query_params['email'])
        return q.all()

    @list_route(methods=['POST'])
    def check_registered(self, request):

        if 'user_id' in request.data:
            user_data = []
            user_details = EmailUser.objects.get(id=request.data['user_id'])
            user = EmailUser.objects.filter(id=request.data['user_id']).values(
                *EMAILUSER_VALUES)
            user_data_dir[
                'is_seller_approved'] = request.user.is_seller_approved

            user_data.append(user_data_dir)
            user_data_dir = {}
            return Response(user_data)
        return Response('false')


class CreateEmailUserViewSet(viewsets.ModelViewSet):
    serializer_class = CreateEmailUserSerializer
    permission_classes = (AllowAny,)
    queryset = EmailUser.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()

    def create(self, validated_data):
        if 'is_social' in self.request.data:
            try:
                user = EmailUser.objects.get(email=self.request.data['email'])
                return JsonResponse({'id':user.id, 'first_name':user.first_name, 'last_name':user.last_name, 'email':user.email,
                                     'is_seller':user.is_seller, 'is_buyer':user.is_buyer, 'token':user.auth_token.key, 'validated_at':user.validated_at})
            except Exception as e:
                user = self.create_user_api(validated_data)
                user.is_social = True
                user.validated_at = datetime.datetime.now()
                user.save()
                return Response(data={'id':user.id, 'token':user.auth_token.key, 'email': user.email,
                                    'is_seller':user.is_seller, 'is_buyer':user.is_buyer, 'validated_at':user.validated_at})
        else:
            user = self.create_user_api(validated_data)
            if user == False:
                user = EmailUser.objects.filter(email=self.request.data['email'])
                if user:
                    return Response(data={'result':'Email id is already exist.'})
            return Response(data={'id':user.id, 'token':user.auth_token.key, 'email': user.email,
                                'is_seller':user.is_seller, 'is_buyer':user.is_buyer, 'validated_at':user.validated_at})

    def create_user_api(self, validated_data):
        serializer = serializers.CreateEmailUserSerializer(
        data=self.request.data
        )
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return False
        user=serializer.save()
        user.set_password(self.request.data['password'])
        user.country_id = user.company_country_id
        user.save()
        if user.is_seller == True:
            user.is_seller_approved = True
            user.save()
        crate_notification_user = FCMDevice.objects.create(registration_id=self.request.data['registration_id'],
                                                           device_id=self.request.data['device_id'],
                                                           user_id=user.id,
                                                           type=self.request.data['type']
                                                           )
        self.send_registration_email()
        return user

    def send_registration_email(self):
        plaintext = get_template('registration_confirmation.txt')
        htmly     = get_template('registration_confirmation.html')

        d = { 'email': self.request.user }

        subject, from_email, to = 'Welcome', settings.DEFAULT_FROM_EMAIL, str(self.request.data['email'])
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

