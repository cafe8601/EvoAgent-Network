---
name: payment-integration
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Payment integration specialist for gateway integration, PCI compliance, and secure transaction processing

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [npm, stripe]
---

# Payment Integration - Tier 2

## Phase 0: Detection
```bash
grep -E "stripe|paypal|square|braintree" package.json requirements.txt 2>/dev/null
find . -path "*/payment/*" -name "*.{js,py}"
```

## Phase 1: Analysis
```bash
grep -r "payment\|checkout\|billing" . --include="*.{js,ts,py}"
find . -name "*stripe*.js" -o -name "*payment*.py"
```

## Phase 2: Implementation
```typescript
// Example: Stripe payment integration
import Stripe from 'stripe';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function createPaymentIntent(amount: number, currency: string) {
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount * 100, // Convert to cents
      currency,
      automatic_payment_methods: {
        enabled: true,
      },
    });

    return {
      clientSecret: paymentIntent.client_secret,
      id: paymentIntent.id
    };
  } catch (error) {
    console.error('Payment error:', error);
    throw new Error('Payment initialization failed');
  }
}

export async function handleWebhook(event: any) {
  switch (event.type) {
    case 'payment_intent.succeeded':
      // Update order status
      await updateOrder(event.data.object.id, 'paid');
      break;
    case 'payment_intent.payment_failed':
      // Notify user
      await notifyPaymentFailed(event.data.object);
      break;
  }
}
```

## Phase 4: Validation
```bash
# Test mode
curl -X POST http://localhost:3000/api/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 10.00, "currency": "usd"}'

# Webhook test
stripe listen --forward-to localhost:3000/api/webhooks
```

## Success Criteria
- [ ] Payment processing working
- [ ] Webhooks configured
- [ ] PCI compliance maintained
- [ ] Error handling complete
- [ ] Test mode verified
