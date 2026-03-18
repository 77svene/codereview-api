import stripe
    import os
    from datetime import datetime
    
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    
    PRICES = {
        "pro": "price_pro_monthly_id",  # $29/mo
        "enterprise": "price_enterprise_monthly_id",  # $199/mo
    }
    
    def create_checkout_session(plan, success_url, cancel_url):
        """Create a Stripe Checkout Session for the specified plan."""
        price_id = PRICES.get(plan)
        if not price_id:
            return {"error": "Invalid plan"}, 400
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"plan": plan}
        )
        
        return {"session_id": session.id, "url": session.url}
    
    def get_customer_portal(customer_id):
        """Create a customer portal session for managing subscriptions."""
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
        )
        return {"url": session.url}
    
    def handle_webhook(payload, sig):
        """Handle Stripe webhook events."""
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        try:
            event = stripe.Webhook.construct_event(payload, sig, webhook_secret)
        except ValueError:
            return {"error": "Invalid payload"}, 400
        except stripe.error.SignatureVerificationError:
            return {"error": "Invalid signature"}, 400
        
        # Handle subscription events
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # Activate the user's account with the selected plan
            print(f"New subscription: {session['metadata']['plan']}")
            
        elif event["type"] == "customer.subscription.deleted":
            # Handle subscription cancellation
            print("Subscription cancelled")
            
        return {"received": True}
    