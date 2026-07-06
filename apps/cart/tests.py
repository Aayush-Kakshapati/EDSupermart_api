from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.cart.models import Cart, CartItem
from threading import Thread
import time

User = get_user_model()

class CartConcurrencyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Test Product', price=10.00, stock=100)

    def test_concurrent_cart_item_addition(self):
        """Test that concurrent additions to the same cart item don't cause race conditions"""
        cart = Cart.objects.create(user=self.user)
        
        def add_item():
            for _ in range(10):
                item, created = CartItem.objects.get_or_create(
                    cart=cart, 
                    product=self.product, 
                    defaults={'quantity': 1}
                )
                if not created:
                    from django.db.models import F
                    CartItem.objects.filter(pk=item.pk).update(quantity=F('quantity') + 1)
                    item.refresh_from_db()
        
        threads = []
        for _ in range(5):
            t = Thread(target=add_item)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 50)  # 5 threads * 10 additions each
