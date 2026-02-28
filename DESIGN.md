# FRAPPE × X402 × MCP 
## AI Tool Marketplace — Technical & Applied Design Document 
**Version 1.0 | February 2026 | Confidential**

---

### What We Are Building
A Frappe-powered open marketplace where MCP tool providers register their AI tools, users pay in fiat (or crypto), and x402 handles automatic per-call monetization — entirely abstracted from the end user.

---

## 1. Vision & Core Concept 

The MCP (Model Context Protocol) ecosystem is growing at an explosive pace — from 100K downloads in Nov 2024 to over 8 million by April 2025, with 5,800+ registered servers. The missing layer is a unified, monetized marketplace where: 

* **Centralized Workspace:** Tool providers register and price their MCP tools in one central workspace. 
* **Autonomous Payments:** AI agents discover and call tools automatically — payments fire without human action. 
* **Fiat On-ramp:** Regular users top up with fiat (UPI, Stripe, credit card) and never touch crypto. 
* **x402 Settlement:** Payments settle via x402 protocol using USDC under the hood. 
* **Frappe Engine:** Frappe provides the entire backend, admin UI, billing, and multi-tenancy. 

> **The Core Insight:** Frappe is not just a backend framework — it IS the product. Its built-in DocTypes, roles, subscriptions, and workspace system map perfectly to a marketplace: users, providers, tools, credits, and audit logs are all native Frappe concepts.

---

## 2. System Architecture 

### 2.1 High-Level Architecture
The system has four distinct layers that work together: 

| Layer | Description |
| :--- | :--- |
| **Frappe Core** | Python/JS backend, DocTypes, REST API, user management, multi-tenancy, billing |
| **MCP Gateway** | HTTP server embedded in Frappe that routes tool calls, resolves tool URLs, returns MCP-compliant responses |
| **x402 Middleware** | Python layer that intercepts every MCP tool call, checks user credits, fires x402 USDC payment, deducts Frappe Credits |
| **Payment Abstraction** | Fiat users pay via Stripe/Razorpay → Frappe credits → USDC pool. Crypto users plug in directly. MoonPay for auto on-ramp. |

### 2.2 Request Flow — Step by Step
When an AI agent calls a tool in the marketplace, this is the exact sequence: 

1. **Request:** AI agent sends MCP tool call to Frappe Workspace endpoint.
2. **Identification:** Frappe MCP Gateway receives request, identifies tool and its registered provider.
3. **Verification:** x402 Middleware checks caller identity and credit balance in Frappe DocType.
4. **Execution:** If balance sufficient: deduct credits, fire x402 USDC payment to provider wallet.
5. **Fallback:** If balance insufficient: return HTTP 402 with payment details (x402 standard).
6. **Proxy:** Frappe forwards the call to the registered MCP tool provider URL.
7. **Audit:** Tool response returned to AI agent. Audit log written in Frappe.

### 2.3 Payment Abstraction Layer
Making crypto invisible to regular users:

| Fiat User Flow | Crypto / Power User Flow |
| :--- | :--- |
| User pays ₹500 via UPI/Stripe | User connects own wallet (MetaMask, Coinbase) |
| Frappe credits account: 500 credits | Set spending limits per session/tool |
| Frappe holds equivalent USDC in pool | x402 fires directly from user wallet |
| Call deducts credits silently | MoonPay auto top-up to keep agent funded |
| User never sees blockchain | Full self-custody, no trust required |

---

## 3. Frappe DocType Design 

### 3.1 Core DocTypes 

| DocType | Key Fields | Purpose |
| :--- | :--- | :--- |
| **MCP Provider** | name, wallet_address, payout_method, verified, rating | Registered tool providers |
| **MCP Tool** | tool_name, provider, endpoint_url, price_per_call, schema_json | Individual tools with pricing |
| **Workspace Credit** | user, balance, total_purchased, currency, wallet_type | Per-user credit balance |
| **Credit Transaction**| user, tool, credits, usdc_amount, timestamp, status | Audit log of calls/payments |
| **Payment Top-Up** | user, fiat_amount, gateway, credits_issued | Fiat payment records |
| **Provider Payout** | provider, period, total_calls, usdc_earned, status | Provider earning summaries |
| **Agent Config** | user, agent_name, spending_limit, whitelist_tools | Per-agent spending policies |

---

## 4. MCP Gateway — Technical Design 

### 4.1 Functionality
The Frappe MCP Gateway is a Python service (Frappe app) exposing a single entry-point for all MCP calls, handling discovery, routing, and payment.

### 4.2 Key Endpoints 

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/mcp/tools/list` | GET | Returns registered tools with pricing/schemas |
| `/mcp/tools/call` | POST | Main entry point — receives call, fires payment, proxies to provider |
| `/mcp/tools/{id}/schema`| GET | Returns JSON schema for a specific tool |
| `/mcp/credits/balance` | GET | Returns current credit balance |
| `/mcp/credits/topup` | POST | Initiates fiat top-up (Stripe/Razorpay) |

### 4.3 x402 Middleware Integration
Wraps `/mcp/tools/call` using standard x402 HTTP 402 flow. The credit deduction and x402 payment fire in a single database transaction. If the USDC transfer fails, credits are **not** deducted.

---

## 5. Fiat Payment Layer 

### 5.1 Credit System Design
Decouples fiat pricing from crypto settlement: 

| Plan | Fiat (INR) | Credits Issued | Bonus |
| :--- | :--- | :--- | :--- |
| Starter | ₹299 | 300 credits | - |
| Builder | ₹999 | 1,100 credits | 10% |
| Pro | ₹2,499 | 3,000 credits | 20% |

### 5.2 Gateways Supported
* **Global:** Stripe, MoonPay, Transak.
* **India:** Razorpay, PayU, BHIM UPI.

---

## 6. Provider Economics 

* **Revenue Split:** 85% Provider | 12% Platform | 3% Network/x402.
* **Payouts:** Instant USDC to wallet, or fiat off-ramp via Transak/Razorpay on threshold ($10/₹500).

---

## 7. Implementation Roadmap 

**Phase 1 — Foundation (Weeks 1–3)** 
* Create `frappe_x402` app skeleton.
* Build core DocTypes (Provider, Tool, Credit).
* Implement MCP Gateway endpoints.
* Integrate x402-python SDK.

**Phase 2 — Marketplace (Weeks 4–6)**
* Provider self-registration UI.
* Public tool discovery catalog.
* Agent spending policies.
* Provider payout automation.

**Phase 3 — Ecosystem (Weeks 7–10)**
* Submit to Frappe Cloud Marketplace.
* Publish to MCP registries (PulseMCP, mcp.so).
* Open source release on GitHub.

---

## 8. Technology Stack 

* **Backend:** Frappe (Python)
* **Protocol:** MCP (Anthropic) + x402 (Coinbase/HTTP 402)
* **Blockchain:** USDC on Base Chain
* **On-Ramp:** Stripe / Razorpay / MoonPay
* **Database:** MariaDB + Redis

---

## 9. Competitive Advantages 

* **Zero Crypto Barrier:** Fiat users never see a wallet or seed phrase.
* **Frappe Native:** Instant access to 40k+ star ecosystem and ERPNext businesses.
* **Agent-Native:** Built for AI-to-AI autonomous commerce.
* **India-Ready:** Day-one UPI support via Razorpay.
