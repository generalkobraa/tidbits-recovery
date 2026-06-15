import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load keys from Environment Variables (Set these in Render)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Soft decline detected for {payment_intent['id']}! Triggering Tidbits.")
        # Add your logic here
        return jsonify(success=True), 200

    return '', 200

# DYNAMIC PORT BINDING FOR RENDER
if __name__ == "__main__":
    # Render provides the PORT environment variable. 
    # If not found (e.g., running locally), default to 10000.
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)