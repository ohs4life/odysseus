---
name: hsa-payments
description: "HSA / FSA payment for OHS orders — only via TrueMed, only one-time purchases (subscriptions not eligible), customer must self-place the order online, OHS employees cannot place the order for the customer. Use this when a customer asks about paying with HSA / FSA, TrueMed, or using pre-tax dollars."
version: 1.0.0
category: ohs-customer-support
status: published
shared: true
owner: ohs-admin
confidence: 0.9
source: user
created: "2026-08-02T18:30:00Z"
---

# OHS — HSA / FSA Payments via TrueMed

## When to Use
When the user (employee or customer) asks any variant of:
- "Can I pay with my HSA / FSA?"
- "Do you accept HSA?"
- "How does TrueMed work?"
- "Can I use my HSA card at checkout?"
- "Can you place the order for me using my HSA?"
- "Are subscriptions HSA-eligible?"

## Procedure

### 1. The headline rules
- OHS offers HSA / FSA payment **only through TrueMed** (a third-party service that verifies eligibility and processes the HSA / FSA payment).
- **Only one-time purchases are eligible** at this time. **Subscriptions are NOT currently eligible** for HSA.
- The customer **must place the order themselves online** while logged into their own OHS account. **OHS employees and customer service reps cannot place the order on the customer's behalf** using HSA as the payment method.
- Orders paid with HSA are **subject to approval from the HSA provider** before OHS can create or fulfill the order. **Orders may be delayed** until payment is authorized.

### 2. The customer journey (at checkout)
1. Customer is logged into their own OHS account at `optimalhealthsystems.com`.
2. Customer reaches the **Checkout** page and goes to the **Payment** section.
3. Customer selects the payment method **"TrueMed - Pay with HSA/FSA"** and clicks **Pay Now**.
4. Customer is directed to the **TrueMed website** to request their HSA account be used as the payment method.
5. TrueMed verifies eligibility with the HSA provider.
6. On approval, the order is created / fulfilled in OHS's system. On denial, OHS is notified and the order may be canceled.

### 3. What you can and cannot do (for OHS employees)
- ✅ **Help the customer understand the process.** Walk them through the steps above.
- ✅ **Direct them to support@optimalhealthsystems.com** if they have a problem with a TrueMed / HSA order.
- ❌ **Cannot place the order yourself using the customer's HSA.** The order must come from the customer's own account.
- ❌ **Cannot override the TrueMed eligibility decision.** If the HSA provider denies the order, OHS cannot force it through.
- ❌ **Cannot retroactively apply HSA** to an order that wasn't placed with HSA as the payment method.

## Pitfalls
- **Do not tell the customer "yes, you can use your HSA card directly at checkout."** It's not a card swipe at OHS's checkout — it goes through TrueMed.
- **Do not tell a customer that subscriptions are HSA-eligible.** They are not (at the time of this writing).
- **Do not place an HSA order on behalf of a customer.** Even with their permission, this violates the policy.
- **Do not promise the order will ship immediately after TrueMed approval.** TrueMed approval is a prerequisite; OHS still has to fulfill the order like any other (standard 48-hour processing, see `ohs-customer-support/shipping-policy`).

## Verification
- Source-of-truth: `knowledgebase/policies/hsa-policies.md`.
- Related: `ohs-customer-support/shipping-policy` (standard order processing time applies after TrueMed approves).

## Anything else

### The verbatim policy (OHS-authored)
> *"We offer options to use an HSA account for purchases of our products. This service is available through TrueMed and there are certain requirements that must be met. Only One-Time purchases are eligible for purchase with HSA at this time. (Subscriptions are not currently eligible). A customer must place the order online while logged in to their own account. OHS Employees and Custom Service Representatives are not able to accept HSA as payment for orders that they (the OHS representative) are placing on behalf of the customer. Orders placed using HSA are subject to approval from the HSA provider before OHS can create or fulfill the order. Orders may be delayed until payment is authorized from HSA provider. Customers can select to use HSA as a payment method on the Checkout page under the 'Payment' section. Select the payment method 'TrueMed - Pay with HSA/FSA' then click 'Pay Now'. The customer will be directed to the TrueMed website to request their HSA account be used as the payment method for the OHS purchase."*

### Why this matters
HSA / FSA dollars are pre-tax and meant for qualified medical expenses. The IRS rules around what counts as a "qualified medical expense" for supplements are strict. TrueMed is OHS's compliance partner that screens purchases for HSA-eligibility under those IRS rules. OHS intentionally routes HSA payments through TrueMed rather than accepting HSA cards directly, to avoid the compliance risk.
