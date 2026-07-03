from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.products.models import Product

from .serializers import CartSerializer, CartItemSerializer
from .models import Cart, CartItem

# Create your views here.
class CartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, create = Cart.objects.get_or_create(user = request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CartItemAddAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'Error: ProductId not valid.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
        except(TypeError , ValueError):
            return Response({'Error': 'Input a valid integer'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(pk= product_id)
        except Product.DoesNotExist:
            return Response({'Error':' product does not exitst'}, status=status.HTTP_404_NOT_FOUND)
        
        cart, create = Cart.objects.get_or_create(user = request.user)

        items, created = CartItem.objects.get_or_create(cart = cart, product = product, defaults={'quantity': quantity})

        if not created:
            items.quantity += quantity
            items.save()

        serializer = CartItemSerializer(items)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    

class CartItemDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):

        try:
            item = CartItem.objects.get(pk = pk, cart__user = request.user)
        except CartItem.DoesNotExist:
            return Response({'Error': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart = item.cart
        item.delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)