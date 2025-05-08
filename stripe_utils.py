import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(user_email):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Bank Statement Conversion'},
                'unit_amount': 500,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:5000/',
        customer_email=user_email,
    )
    return session
