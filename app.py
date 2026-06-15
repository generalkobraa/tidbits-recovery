import os
from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)

# Load your keys from the environment variables (Render/Railway settings)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return jsonify(success=False), 400

    # Handle the 'payment_intent.payment_failed' event
    if event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        decline_code = intent['last_payment_error'].get('decline_code')

        # Logic: Only trigger if the decline is a "soft" failure
        if decline_code in ['insufficient_funds', 'try_again_later']:
            # Here you would trigger your email or frontend notification
            # For this example, we log it
            print(f"Soft decline detected for {intent['amount']}! Triggering Tidbits.")
            
            # Initiate the 25% charge logic (Placeholder for your specific user ID)
            # You would link this to the customer's saved payment method
            
    return jsonify(success=True), 200

if __name__ == '__main__':
    app.run(port=4242)