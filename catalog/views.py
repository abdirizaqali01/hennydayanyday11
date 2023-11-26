from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from .models import Order
import json
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def landing_page(request):
    return render(request, 'landingPage.html')

def loader(request):
    return render(request, 'loader.html')

def shop(request):
    return render(request, "shop.html")

def success(request):
    return render(request, "thankyou.html")

def unsuccess(request):
    return render(request, "unsuccessful.html")

def error(request, undefined_path):
    return render(request, '404.html')

def calculate_total_amount(basket):
    total = 0

    # Iterate through each item in the basket
    for item in basket:
        try:
            # Retrieve the price details from Stripe using the price ID
            price_id = item.get('id')
            price = stripe.Price.retrieve(price_id)

            # Add the product of the price and quantity to the total
            total += price.unit_amount * item.get('quantity')

        except stripe.error.StripeError as e:
            # Handle any errors that may occur during the Stripe API request
            print(f"Error fetching price {price_id}: {e}")

    # Convert the total from cents to dollars
    total = total / 100
    return total

@csrf_protect
def checkout(request):
    if request.method == 'POST':
        try:
            # Retrieve the JSON data sent in the request
            data = json.loads(request.body)

            # Access the basket data
            basket = data.get('basket', [])

            # Calculate the total amount from the basket (customize as per your product structure)
            total_amount = calculate_total_amount(basket)

            # Create a new Order instance and save it to the database
            order = Order.objects.create(
                basket_data=basket,
                total_amount=total_amount,
            )

            # Create a Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_options={
                    "card": {
                        "setup_future_usage": "on_session",
                    }
                },
                line_items=[
                    {
                        'price': item['id'],
                        'quantity': item['quantity'],
                    }
                    for item in basket
                ],
                shipping_address_collection={
                    "allowed_countries": [
                        'AC', 'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA',
                        'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV',
                        'BW', 'BY', 'BZ', 'CA', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CV', 'CW',
                        'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ',
                        'FK', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR',
                        'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ',
                        'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KR', 'KW', 'KY', 'KZ', 'LA',
                        'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MK',
                        'ML', 'MM', 'MN', 'MO', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NC', 'NE',
                        'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM',
                        'PN', 'PR', 'PS', 'PT', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG', 'SH',
                        'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SZ', 'TA', 'TC', 'TD', 'TF',
                        'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY',
                        'UZ', 'VA', 'VC', 'VE', 'VG', 'VN', 'VU', 'WF', 'WS', 'XK', 'YE', 'YT', 'ZA', 'ZM', 'ZW', 'ZZ']
                },
                mode='payment',
                success_url='http://127.0.0.1:8000/success',
                cancel_url='http://127.0.0.1:8000/unsuccess',
            )

            return JsonResponse({'checkout_url': checkout_session.url})

        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except stripe.error.StripeError as e:
            return JsonResponse({'status': 'error', 'message': f'Stripe Error: {e}'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    