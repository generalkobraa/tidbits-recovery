import os
import stripe
import resend  # You will need to install this: pip install resend
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure API Keys
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
resend.api_key = os.getenv('RESEND_API_KEY')

def send_receipt_email(customer_email, intent_id, status):
    """Sends a receipt or failure notice to the customer."""
    subject = "Payment Update regarding your Tidbits purchase" if status == "failed" else "Your Tidbits Receipt"
    html_content = f"<p>Your payment {intent_id} has <b>{status}</b>.</p>"
    
    resend.Emails.send({
        "from": "noreply@yourdomain.com", # Change to your verified domain
        "to": customer_email,
        "subject": subject,
        "html": html_content
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception:
        return jsonify({'error': 'Invalid request'}), 400

    # Event 1: Payment Failed
    if event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        customer_email = payment_intent.get('receipt_email') or "customer@example.com"
        send_receipt_email(customer_email, payment_intent['id'], "failed")
        print(f"Failed payment email sent to {customer_email}")

    # Event 2: Payment Succeeded (The Receipt)
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        customer_email = payment_intent.get('receipt_email') or "customer@example.com"
        send_receipt_email(customer_email, payment_intent['id'], "succeeded")
        print(f"Success receipt email sent to {customer_email}")

    return jsonify(success=True), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4242))
    app.run(host='0.0.0.0', port=port)