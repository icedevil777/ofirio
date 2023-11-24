from django.http import JsonResponse
from django.views import View
from django.core.cache import cache


class GetCSRF(View):

    def get(self, request):

        access = cache.get("access")
        print(access)
        access = 'ty2DDGGfi8MyDGRfLXLbtDzR4GWWzV91ZP8MyYfucTZGU7BpkrYPizani0eDiA2G'
        return JsonResponse({'key': access}, safe=True)


class SocialUrls(View):

    def get(self, request):

        urls = {
            'facebook': "https://www.facebook.com/login",
            'google': "https://accounts.google.com/login",
            'twitter': "https://twitter.com/login",
        }
        return JsonResponse({'key': urls}, safe=True)


class Subscription(View):

    def get(self, request):

        dto = {
            'current_period_start': "2022-01-01",
            'current_period_end': "2025-01-31",
            'status': "active",
            'invoices': [
                {
                    'id': "invoice_123",
                    'amount': 50.00,
                    'date': "2022-01-15"
                },
                {
                    'id': "invoice_456",
                    'amount': 50.00,
                    'date': "2022-02-15"
                }
            ],
            'card_last_4': "1234",
            'next_payment_amount': 50.00,
            'cancel_at_period_end': False
        }
        return JsonResponse({'key': dto}, safe=True)
