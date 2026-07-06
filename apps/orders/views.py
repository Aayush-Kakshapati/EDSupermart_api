from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import IsOwnerOrStaff, IsOwner
from .utils import process_new_order, clear_user_cart


class OrderListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'owner' or request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get(self, request, pk):
        try:
            if request.user.role == 'owner' or request.user.is_staff:
                order = Order.objects.get(pk=pk)
            else:
                order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        if not data.get('email'):
            data['email'] = request.user.email
        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            clear_user_cart(request.user)
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


class OrderUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def patch(self, request, pk):
        try:
            if request.user.role == 'owner' or request.user.is_staff:
                order = Order.objects.get(pk=pk)
            else:
                order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderStatusUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            old_status = order.status
            status_value = request.data.get('status')
            if not status_value:
                return Response(
                    {'error': 'Status field is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if status_value not in [choice[0] for choice in Order.Status.choices]:
                return Response(
                    {'error': 'Invalid status value'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = status_value
            order.save()
            
            # Create notification for user when order is shipped
            if old_status != 'shipped' and status_value == 'shipped':
                Notification.objects.create(
                    user=order.user,
                    type=Notification.Type.ORDER_SHIPPED,
                    title=f"Order #{order.id} Shipped",
                    message=f"Your order #{order.id} has been shipped and is on its way!",
                    order_id=order.id
                )
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            if order.status != Order.Status.PENDING:
                return Response(
                    {'error': 'Can only delete pending orders'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.delete()
            return Response(
                {'message': 'Order deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderConfirmDeliveryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            if order.status != Order.Status.SHIPPED:
                return Response(
                    {'error': 'Can only confirm delivery for shipped orders'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = Order.Status.DELIVERED
            order.save()
            
            # Create notification for owner
            from apps.accounts.models import User
            owners = User.objects.filter(role='owner')
            for owner in owners:
                Notification.objects.create(
                    user=owner,
                    type=Notification.Type.ORDER_DELIVERED,
                    title=f"Order #{order.id} Delivered",
                    message=f"Order #{order.id} has been delivered and confirmed by {order.user.username}",
                    order_id=order.id
                )
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
