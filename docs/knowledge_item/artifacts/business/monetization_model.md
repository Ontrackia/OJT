# Monetization & Licensing Model

OnTrackIA uses a subscription-based model (SaaS) with native Stripe integration and feature-based access control (Gatekeeper).

## 💳 Stripe Integration

The system leverages the **Stripe SDK** to manage organization-level subscriptions.

### Billing Services

- **Checkout Sessions**: Generates secure Stripe-hosted checkout links.
- **Customer Portal**: Allows self-service management for billing and invoices.
- **Webhooks**: Automated processing for checkout completion and subscription lifecycle events.

## 🏗️ Licensing Tiers

The `Tenant` model tracks the subscription status and tier:

| Tier | Features | Requirement |
| :--- | :--- | :--- |
| **Basic** | OJT Traceability, Manual PDF Generation | Standard |
| **Pro** | AI Senior Auditor Coach, Automated PDF Overlays | Advanced |
| **Ultimate** | QMS-SMS Full Suite, Advanced Analytics | Top Tier |

*Note: The "Ultimate" tier replaces legacy nomenclature to align with current branding standards.*

## 🛡️ Gatekeeper Protocol

Access to premium features (like AI RCA validation) is enforced via the **Gatekeeper Middleware**.

- **Enforcement**: Checks `subscription_tier` and `billing_status` at the request level.
- **Fail-Safe**: If a tenant's subscription expires, features are automatically gated to the Basic tier without data loss.
