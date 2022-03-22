import stripe
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from stripebank.api.serializers import StripeNotificationSerializer


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]  # validation is done later by stripe library

    def post(self, request, *args, **kwargs):
        payload = request.body.decode(request.encoding or 'utf-8')
        stripe.api_key = settings.STRIPE_API_KEY
        sig_header = request.headers.get('STRIPE_SIGNATURE')

        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)

        if event['type'] == 'checkout.session.completed':
            serializer = StripeNotificationSerializer(data={
                **event['data']['object'],
                'raw': event,
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({'success': True})
