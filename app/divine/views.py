from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
# from django.shortcuts import render
# from django.urls import reverse_lazy
# from django.views.generic import CreateView, UpdateView, ListView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .backends import UnsafeSessionAuthentication
from .models import RawMaterials, FinishedGoods, Compositions, JobCards
from .serializers import RawMaterialsSerializer, FinishedGoodsSerializer, \
    CompositionsSaveSerializer, CompositionServeSerializer, UserSerializer, \
    JobCardsSerializer
from .permissions import CustomModelPermissions
from rest_framework import viewsets, permissions, status
import pyotp

# from .forms import RawMaterialForm, FinishedGoodsForm
# from .models import RawMaterials


class Register(APIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    @staticmethod
    def post(request):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save()
            uri = pyotp.totp.TOTP(serialized.data['mfa_hash']).provisioning_uri(serialized.data['email'],issuer_name="Divine Goods Management")
            qrcode_uri = "https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl={}".format(uri)
            return JsonResponse({
                'message':'User Created Successfully',
                'qrcode': qrcode_uri
            }, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (UnsafeSessionAuthentication,)

    @staticmethod
    def post(request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        otp = data.get('otp', None)
        user = authenticate(username=email, password=password)
        if user:
            totp = pyotp.TOTP(user.mfa_hash)
            if totp.verify(otp):
                login(request, user)
                serializer = UserSerializer(user)
                return JsonResponse({
                    'user': serializer.data,
                    'message':'User authenticated Successfully'
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'message':'Invalid OTP'
                }, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return JsonResponse({
                'message':'Invalid email/password'
            }, status=status.HTTP_401_UNAUTHORIZED)

# class Login(APIView):
#     permission_classes = (AllowAny,)
#     authentication_classes = (UnsafeSessionAuthentication,)
#
#     @staticmethod
#     def post(request):
#         username = request.data.get("username")
#         password = request.data.get("password")
#
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             login(request, user)
#             serializer = UserSerializer(user)
#             return JsonResponse({
#                 "auth": True,
#                 "user": serializer.data
#             }, status=status.HTTP_200_OK)
#
#         return JsonResponse({
#             "auth": False
#         }, status=status.HTTP_401_UNAUTHORIZED)


class CheckSession(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return JsonResponse({
                "auth": True,
                "user": serializer.data
            })
        else:
            return JsonResponse({
                "auth": False
            }, status=status.HTTP_401_UNAUTHORIZED)


class Logout(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (UnsafeSessionAuthentication,)

    @staticmethod
    def delete(request):
        logout(request)
        return JsonResponse({
            "auth": False
        })


class RawMaterialsViewSet(viewsets.ModelViewSet):
    queryset = RawMaterials.objects.all()
    serializer_class = RawMaterialsSerializer
    permission_classes = (AllowAny,)


class FinishedGoodsViewSet(viewsets.ModelViewSet):
    queryset = FinishedGoods.objects.all()
    serializer_class = FinishedGoodsSerializer
    permission_classes = (AllowAny),


class CompositionsView(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    queryset = Compositions.objects.all()

    @staticmethod
    def create(request) -> JsonResponse:
        data = request.data
        if isinstance(data, object) & isinstance(data['fg_id'], str) & \
                isinstance(data['rm'], list):
            serialized_data = []
            for rm in data['rm']:
                serialized_data.append({
                    "fg": data['fg_id'], "rm": rm['rm_id'],
                    "quantity": rm['quantity'], "unit": rm['unit']
                })
            serializer = CompositionsSaveSerializer(data=serialized_data, many=True)
            if serializer.is_valid():
                try:
                    finished_good = FinishedGoods.objects.get(pk=data['fg_id'])
                except FinishedGoods.DoesNotExist:
                    finished_good = None
                if finished_good is not None:
                    finished_good.composition_exists = True
                    finished_good.price = 0
                    total_quantity = 0
                    for comp_rm in data['rm']:
                        try:
                            rm_obj = RawMaterials.objects.get(pk=comp_rm['rm_id'])
                        except RawMaterials.DoesNotExist:
                            rm_obj = None
                        comp_rm_quantity = 0
                        try:
                            comp_rm_quantity = float(comp_rm['quantity'])
                        except ValueError:
                            pass
                        if rm_obj is not None and comp_rm_quantity > 0:
                            quantity_multiplier = 1
                            try:
                                unit = comp_rm['unit']
                                if unit == 'GM':
                                    quantity_multiplier = 0.001
                                if unit == 'MG':
                                    quantity_multiplier = 0.000001
                            except KeyError:
                                pass
                            total_quantity += comp_rm_quantity * quantity_multiplier
                            finished_good.price = finished_good.price + rm_obj.price * \
                                                  comp_rm_quantity * quantity_multiplier
                    finished_good.price = finished_good.price / total_quantity
                    finished_good.save()
                    existing_composition = Compositions.objects.filter(fg_id=data['fg_id'])
                    existing_composition.delete()
                    serializer.save()
                    return JsonResponse({
                        "message": "success"
                    }, status=status.HTTP_200_OK)
                return JsonResponse({
                    "message": "Finished Good does not Exist"
                }, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({
                "message": "Invalid Composition"
            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            "message": "Malformed Request"
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk) -> JsonResponse:
        if isinstance(pk, str):
            if len(self.queryset) > 0:
                composition = self.queryset.filter(fg_id=int(pk))
                serializer = CompositionServeSerializer(composition, many=True)
                return JsonResponse({
                    "composition": serializer.data
                })
            else:
                return JsonResponse({
                    "composition": []
                })
        return JsonResponse({
            "message": "Malformed Request"
        }, status=status.HTTP_400_BAD_REQUEST)


class JobCardsViewSet(viewsets.ModelViewSet):
    queryset = JobCards.objects.all()
    serializer_class = JobCardsSerializer
    permission_classes = (AllowAny,)


class CompositionSearchViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated, ]
    queryset = Compositions.objects.all()

    def retrieve(self, request, pk) -> JsonResponse:
        if isinstance(pk, str):
            if len(self.queryset) > 0:
                matched_comp = self.queryset.filter(rm__rm_name__icontains=pk)
                matched_comp_serializer = CompositionsSaveSerializer(matched_comp, many=True)
                return JsonResponse({
                    "composition": matched_comp_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "message": "Internal Server Error"
                }, status=status.HTTP_501_NOT_IMPLEMENTED)
        return JsonResponse({
            "message": "Malformed Request"
        }, status=status.HTTP_400_BAD_REQUEST)


# class CompositionsViewSet(viewsets.ModelViewSet):
#     queryset = Compositions.objects.all()
#     serializer_class = CompositionsSerializer
#     permission_classes = [permissions.IsAuthenticated, ]

# class RawMaterialsCreateView(CreateView):
#     model = RawMaterials
#     form_class = RawMaterialForm
#     success_url = reverse_lazy('raw_materials_list')

# class RawMaterialsListView(ListView):
#     model = RawMaterials
#     context_object_name = 'raw_materials'

# class RawMaterialsUpdateView(UpdateView):
#     model = RawMaterials
#     form_class = RawMaterialForm
#     template_name = 'divine/rawmaterials_update_form.html'
#     success_url = reverse_lazy('raw_materials_list')

# class FinishedGoodsCreateView(CreateView):
#     model = FinishedGoods
#     form_class = FinishedGoodsForm
#     success_url = reverse_lazy('composition_add')

# class FinishedGoodsListView(ListView):
#     model = FinishedGoods
#     context_object_name = 'finished_goods'

# class FinishedGoodsUpdateView(UpdateView):
#     model = FinishedGoods
#     form_class = FinishedGoodsForm
#     template_name = 'divine/finishedgoods_update_form.html'
#     success_url = reverse_lazy('finished_goods_list')
