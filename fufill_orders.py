import shopify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Shopify API Credentials
SHOPIFY_API_KEY = 'your_api_key'
SHOPIFY_API_PASSWORD = 'your_api_password'
SHOPIFY_STORE_NAME = 'your_store_name'
SHOPIFY_API_VERSION = '2023-04'

# SMTP Email Credentials
SMTP_SERVER = 'smtp.your_email_provider.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_email@example.com'
SMTP_PASSWORD = 'your_email_password'

# Initialize Shopify API Session
shop_url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_API_PASSWORD}@{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}"
shopify.ShopifyResource.set_site(shop_url)

def get_unfulfilled_orders():
    orders = shopify.Order.find(fulfillment_status='unfulfilled')
    return orders

def send_email(customer_email, customer_name, order_number):
    subject = f"Your Order #{order_number} has been fulfilled"
    body = f"Dear {customer_name},\n\nYour order #{order_number} has been fulfilled. Thank you for shopping with us!"

    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = customer_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

def fulfill_order(order):
    location_id = get_location_id()  # Fetch the correct location ID
    fulfillment = shopify.Fulfillment({
        'order_id': order.id,
        'location_id': location_id,
        'tracking_numbers': [],  # You can add tracking numbers here if available
        'line_items': [{'id': line_item.id} for line_item in order.line_items]
    })
    fulfillment.save()

def get_location_id():
    locations = shopify.Location.find()
    if locations:
        return locations[0].id  # Return the first location ID
    else:
        raise Exception("No locations found in Shopify store.")

def main():
    orders = get_unfulfilled_orders()
    for order in orders:
        customer_email = order.email
        customer_name = order.customer.first_name
        order_number = order.name

        # Send email to customer
        send_email(customer_email, customer_name, order_number)

        # Fulfill order on Shopify
        fulfill_order(order)
        print(f"Order #{order_number} fulfilled and email sent to {customer_email}")

if __name__ == "__main__":
    main()
