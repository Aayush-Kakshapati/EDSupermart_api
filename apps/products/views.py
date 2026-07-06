from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Product
from .permissions import IsOwner
from .serializers import ProductSerializer
from apps.orders.serializers import OrderCreateSerializer, OrderSerializer
from apps.orders.utils import process_new_order


class ProductListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def post(self, request):        
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def patch(self, request, pk):
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def delete(self, request, pk):
        product = Product.objects.get(pk=pk)
        
        product.delete()
        return Response(
            {'message': 'Product deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class ProductBuyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            quantity = int(request.data.get('quantity', 1))
        except (TypeError, ValueError):
            return Response(
                {'error': 'Quantity must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be a positive integer'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {
            'email': request.user.email,
            'items': [{'product_id': pk, 'quantity': quantity}],
        }
        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            process_new_order(order)
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        errors = serializer.errors
        if 'items' in errors:
            detail = errors['items']
            if isinstance(detail, list) and detail:
                message = str(detail[0])
            else:
                message = str(detail)
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
