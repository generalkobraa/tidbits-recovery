import os
import stripe
import resend
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure API Keys from environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
resend.api_key = os.getenv('RESEND_API_KEY')

def send_receipt_email(customer_email, intent_id, status):
    """Sends a professional receipt or failure notice to the customer."""
    subject = "Payment Update regarding your Tidbits purchase" if status == "failed" else "Your Tidbits Receipt"
    html_content = f"<p>Your payment <b>{intent_id}</b> has <b>{status}</b>.</p>"
    
    try:
        resend.Emails.send({
            "from": "noreply@yourdomain.com", # Ensure this domain is verified in Resend
            "to": customer_email,
            "subject": subject,
            "html": html_content
        })
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    # Capture raw payload for signature verification
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify the signature
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle Events
    # Stripe objects use dot notation (e.g., event.data.object.id)
    payment_intent = event.data.object

    if event.type == 'payment_intent.payment_failed':
        # Safely get receipt_email; default to a fallback
        customer_email = getattr(payment_intent, 'receipt_email', "customer@example.com")
        send_receipt_email(customer_email, payment_intent.id, "failed")
        print(f"Failed payment handled for {payment_intent.id}")

    elif event.type == 'payment_intent.succeeded':
        # Safely get receipt_email; default to a fallback
        customer_email = getattr(payment_intent, 'receipt_email', "customer@example.com")
        send_receipt_email(customer_email, payment_intent.id, "succeeded")
        print(f"Success receipt handled for {payment_intent.id}")

    return jsonify(success=True), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4242))
    app.run(host='0.0.0.0', port=port)