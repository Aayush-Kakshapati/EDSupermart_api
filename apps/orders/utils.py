from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone


def clear_user_cart(user):
    from apps.cart.models import Cart

    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart.cart_items.all().delete()


def process_new_order(order):
    from apps.accounts.models import User
    from apps.notifications.models import Notification

    send_order_confirmation_email(order)

    Notification.objects.create(
        user=order.user,
        type=Notification.Type.ORDER_PLACED,
        title=f"Order #{order.id} Placed",
        message=(
            f"Your order has been placed successfully. "
            f"Total: Rs. {order.total_amount}. We'll notify you when it ships."
        ),
        order_id=order.id,
    )

    owners = User.objects.filter(role='owner')
    for owner in owners:
        Notification.objects.create(
            user=owner,
            type=Notification.Type.NEW_ORDER,
            title=f"New Order #{order.id}",
            message=(
                f"New order from {order.user.username}. "
                f"Phone: {order.user.phone}, "
                f"Address: {order.user.address if order.user.address else 'Not provided'}. "
                f"Total: Rs. {order.total_amount}"
            ),
            order_id=order.id,
        )


def send_order_confirmation_email(order):

    local_time = timezone.localtime(order.created_at)
    formatted_time = local_time.strftime('%B %d, %Y at %I:%M %p')

    subject = f'Order Confirmation - Order #{order.id}'
    
    items_html = ""
    for item in order.order_items.all():
        items_html += f"""
        <tr>
            <td>{item.product.name}</td>
            <td>{item.quantity}</td>
            <td>Rs. {item.price}</td>
            <td>Rs. {item.quantity * item.price}</td>
        </tr>
        """
    
    html_message = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .order-details {{ background-color: #f9f9f9; padding: 20px; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #4CAF50; color: white; }}
            .total {{ font-size: 18px; font-weight: bold; text-align: right; }}
            .footer {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Order Confirmation</h1>
                <p>Order #{order.id}</p>
            </div>
            
            <div class="order-details">
                <h2>Order Details</h2>
                <p><strong>Status:</strong> {order.get_status_display()}</p>
                <p><strong>Email:</strong> {order.email}</p>
                <p><strong>Address:</strong> {order.user.address if order.user.address else 'Not provided'}</p>
                <p><strong>Order Date:</strong> {formatted_time}</p>
            </div>
            
            <h3>Items Ordered</h3>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div class="total">
                <p>Total Amount: Rs.{order.total_amount}</p>
            </div>
            
            <div class="footer">
                <p>If any details are incorrect, please contact us immediately:</p>
                <p><strong>Phone:</strong> {settings.CONTACT_PHONE_NUMBER}</p>
                <p><strong>Email:</strong> {settings.EMAIL_HOST_USER}</p>
                <p>Thank you for your order!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    plain_message = f"""
Order Confirmation - Order #{order.id}

Order Details:
Status: {order.get_status_display()}
Email: {order.email}
Address: {order.user.address if order.user.address else 'Not provided'}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}

Items Ordered:
"""
    
    items = order.order_items.select_related("product").all()
    for item in items:
        plain_message += f"- {item.product.name} x {item.quantity} = Rs. {item.quantity * item.price}\n"
    
    plain_message += f"\nTotal Amount: Rs. {order.total_amount}\n"
    plain_message += "\nIf any details are incorrect, please contact us immediately:\n"
    plain_message += f"Phone: {settings.CONTACT_PHONE_NUMBER}\n"
    plain_message += f"Email: {settings.EMAIL_HOST_USER}\n"
    plain_message += "Thank you for your order!"
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [order.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
