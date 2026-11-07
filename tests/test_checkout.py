import os
import tempfile
import unittest

from config import Config


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class CheckoutTaxesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        TestConfig.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(self.tmp, 'test.db')
        TestConfig.UPLOAD_FOLDER = os.path.join(self.tmp, 'uploads')
        from app import create_app, db
        self.db = db
        self.app = create_app(TestConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.db.session.remove()
        self.ctx.pop()

    def test_checkout_guarda_desglose(self):
        from app.models.user import User, Address
        from app.models.product import Product
        from app.models.order import CartItem, Order

        user = User.query.filter_by(email='admin@example.com').first()
        self.db.session.add(Address(user_id=user.id, street='Calle 1', city='CDMX',
                                    state='CDMX', zipcode='01000', is_default=True))
        refresco = Product(name='Refresco 600 ml', description='x', price=20, stock=10,
                           category_id=1, tax_profile='bebida_azucarada', ieps_units=0.6)
        self.db.session.add(refresco)
        self.db.session.commit()
        self.db.session.add(CartItem(user_id=user.id, product_id=refresco.id, quantity=2))
        self.db.session.commit()
        address = Address.query.filter_by(user_id=user.id).first()

        client = self.app.test_client()
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        client.post('/checkout', data={'address_id': address.id, 'payment_method': 'oxxo'})

        order = Order.query.order_by(Order.id.desc()).first()
        self.assertIsNotNone(order)
        self.assertAlmostEqual(order.total_amount, 40 + 99, places=2)  # menos de $499: cobra envío
        self.assertAlmostEqual(order.shipping_cost, 99, places=2)
        self.assertAlmostEqual(order.ieps_amount, 3.70, places=2)
        self.assertAlmostEqual(order.subtotal + order.ieps_amount + order.iva_amount,
                               order.total_amount, places=2)
        self.assertEqual(order.items[0].tax_profile, 'bebida_azucarada')


if __name__ == '__main__':
    unittest.main()
