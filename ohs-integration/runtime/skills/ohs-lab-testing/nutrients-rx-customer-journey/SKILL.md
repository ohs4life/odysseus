---
name: nutrients-rx-customer-journey
description: "End-to-end customer journey for the Nutrients Rx program — from creating an OHS account to receiving a Custom Health Pak based on blood + DNA results. Use this when a customer asks 'how does Nutrients Rx work?', 'what happens after I order?', 'how do I get my blood drawn?', or 'how do I see my results?'."
version: 1.0.0
category: ohs-lab-testing
status: published
shared: true
owner: ohs-admin
confidence: 0.95
source: user
created: "2026-08-02T18:30:00Z"
---

# Nutrients Rx — Customer Journey

## When to Use
When the user (customer, sales rep, or new employee) asks any variant of:
- "How does Nutrients Rx work?"
- "What happens after I buy?"
- "How do I get my blood drawn?"
- "How do I see my results?"
- "How do I get my custom pak?"
- "How long does it take?"
- "Where do I find a lab?"
- "Is there a questionnaire?"
- "What's the PSC Hold?"

## Procedure

### Step 1 — Create an OHS account (free, required)
- The customer must have an account on `optimalhealthsystems.com` before purchasing Nutrients Rx.
- If they don't have one, they create a free account first.
- The account is required so the order, the lab report, and the custom pak can be linked.

### Step 2 — Buy Nutrients Rx
- Log in to `optimalhealthsystems.com`.
- Use the search bar (magnifying glass, top-right). Search for the word "nutrients."
- Select **"Nutrients Rx. Lab Work"** from the results.
- Add to cart → review cart → click **Checkout**.
- **Important constraint:** Nutrients Rx can only be purchased on one account. If a family member wants their own, they need their own account.
- Choose a shipping method. If the customer lives near the Pima, AZ facility, they may choose **"Pickup Instore"**.
- Add a shipping address.
- Enter payment. (For HSA / FSA, see `ohs-customer-support/hsa-payments` — must use TrueMed, customer must self-place the order.)
- Click **Pay Now** to complete the purchase.

### Step 3 — Three confirmation emails arrive
After purchase, the customer receives three emails:
1. **Order Confirmation** — order details + order number.
2. **Subscription Enrollment Confirmation** — confirms the Nutrients Rx subscription enrollment.
3. **Nutrients Rx Welcome Email** — contains the link to "Get Started" and activate the Nutrients Rx portal.

> *Note: OHS emails may land in spam. Tell customers to check the spam folder if they don't see the emails in the main inbox.*

### Step 4 — Register the Nutrients Rx portal
- Open the **Nutrients Rx. Portal** email → click **Get Started**.
- Fill out the profile registration page.
- **Password requirements:** at least **12 characters** long, including uppercase + lowercase + numbers + special characters (e.g., `!@#$%^&*`).
- Click **Register**.
- A popup asks the customer to verify their email. Click the verification email → click **Verify Email**.
- A **4-character code** is sent to the email. Enter it to verify. (Memorize / copy / write it down — example code, not real.)

### Step 5 — Complete the 34-question questionnaire
- The customer answers **34 questions** to fully access the Nutrients Rx Portal.
- If the customer needs to pause, progress is **saved** — they can log back in and resume.

### Step 6 — Print the PSC Hold and find a lab
After the questionnaire:
- Click **"Download Document"** to print the **PSC Hold** (a mandatory document required by the lab at the blood draw).
- Click **"Find a Lab"** → enter an address or zip code → find a nearby lab.
- Click **"Make Appointment"** to schedule.
- If the customer lives near **Pima, AZ** (the OHS HQ), they may contact OHS to schedule a blood draw in **OHS's private lab** instead of going to an outside lab.

### Step 7 — At the lab appointment
- **Bring the printed PSC Hold document** to the appointment.
- The blood draw is performed.

### Step 8 — Wait for results (~2 weeks)
- Blood-draw results post to the Nutrients Rx portal **within ~2 weeks** of the blood draw.
- The customer receives an email notification when results are ready.

### Step 9 — View the report
- Open the email → click **"View Recommendations"**.
- Or log in directly to the Nutrients Rx portal.

### Step 10 — Order the Custom Health Pak
- Inside the results email is a **"Buy Customized Pak"** button.
- The Custom Health Pak is **not included** in the Nutrients Rx purchase — it's a separate purchase.
- **Critical:** the custom pak is **created only after the customer places the order**. It is built from the customer's blood (and DNA, if added) results.

### Step 11 — Review the recommendations
After ordering, the customer can see:
- **Recommendations tab** — the specific nutrients included in the personalized health pak.
- **Complementary product recommendations** (scroll down) — additional products that may support the customer's health goals.
- **Detailed Blood Work Results** — the blood work in a color-coded format showing **optimal, functional, and clinical** ranges for each marker.
- **Question-mark icons next to marker titles** — click for an explanation of any marker.
- **Short videos** — additional explanation for selected markers.

## Pitfalls
- **The custom pak is not automatic.** It is not included in Nutrients Rx. The customer must click "Buy Customized Pak" (a separate purchase) after seeing results.
- **The custom pak is built to order.** Per OHS, the custom pak is created *after* the order is placed. Don't promise same-day fulfillment.
- **The Nutrients Rx portal is separate from the OHS store account.** Login to `nutrientsrx.com` (not `optimalhealthsystems.com`) for the portal. **2FA is required every login** — a 4-digit code is emailed each time.
- **The PSC Hold is mandatory at the lab.** Customer must print and bring it.
- **Subscriptions are not HSA-eligible** (see `ohs-customer-support/hsa-payments`). The Nutrients Rx subscription enrollment email may be confusing on this point.
- **Do not interpret results for the customer.** See `ohs-compliance/disclaimers` — describe what's on the report, route medical interpretation to the customer's provider.

## Verification
- Source-of-truth: `knowledgebase/labs/labs-customer-process.txt` (OHS-authored step-by-step guide).
- Related: `ohs-lab-testing/panel-catalog` (what's measured), `ohs-lab-testing/optimal-dna-overview` (DNA add-on), `ohs-products/nutrients-rx` (the SKU), `ohs-products/nutrients-rx-custom-pak` (the output), `ohs-customer-support/contact-info` (for questions).

## Anything else

### Quick answers
- **"How long until I see my results?"** About 2 weeks from the blood-draw date.
- **"Where do I go for the blood draw?"** Search for a lab in the Nutrients Rx portal; or visit OHS's private lab in Pima, AZ if you're local.
- **"Do I need an appointment?"** Yes — make one through the "Find a Lab" tool in the portal.
- **"What do I bring?"** The printed PSC Hold document.
- **"Is the custom pak included?"** No — it's a separate purchase after results are posted.
- **"How do I log back in?"** `nutrientsrx.com` → email + password → 4-digit code via email (2FA every time).

### Login quirk: 2FA every login
Every Nutrients Rx portal login requires a fresh 4-digit code via email. The customer should expect this every time — it's not optional, and there's no "remember this device" option. If the code doesn't arrive, check spam, then request a new code from the login screen.
