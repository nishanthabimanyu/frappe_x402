# frappe_x402

A high-performance economic gateway for the Model Context Protocol (MCP), powered by the Frappe Framework and the x402 payment protocol.

## Overview

frappe_x402 provides a robust marketplace and monetization layer for AI tools. It enables developers to register MCP-compliant services and monetize them using the x402 protocol, allowing autonomous AI agents to discover, invoke, and pay for capabilities on a per-call basis. By bridging the gap between Web2 payment gateways and Web3 settlements, it facilitates seamless "Agentic Commerce."

## Core Features

- **Economic Interceptor:** A specialized middleware that validates user credits and triggers x402 payments before proxying requests to tool providers.
- **MCP Standard Compatibility:** Built specifically for the Model Context Protocol, providing standardized tool discovery and execution.
- **Fiat-to-USDC Abstraction:** Integrated support for Razorpay to handle fiat top-ups, which are internally tracked as credits and settled as USDC on the Base blockchain.
- **Autonomous Governance:** Granular control over AI agent behavior through daily spending limits and tool whitelisting.
- **Unified Ledger:** A persistent audit trail of all tool invocations, credit deductions, and on-chain transaction hashes.

## Project Development Checkpoints

The following milestones have been achieved in the current implementation:

- **Phase 1: Foundation**
    - [x] Application scaffolding and workspace initialization.
    - [x] Implementation of core DocTypes: MCP Provider, MCP Tool, Workspace Credit, Credit Transaction.
    - [x] Database migration and multi-tenant schema verification.

- **Phase 2: Economic Gateway**
    - [x] Development of the Economic Interceptor middleware.
    - [x] Integration of x402 protocol for USDC settlement (Base Mainnet ready).
    - [x] Implementation of Razorpay fiat-to-credit bridge.
    - [x] Authenticated API access via Frappe Key/Secret system.

- **Phase 3: User Interface**
    - [x] Design and implementation of the Marketplace "App Store" UI.
    - [x] Deployment of the x402 Marketplace Workspace (Frappe v15 compatible).
    - [x] Real-time credit balance tracking and transaction audit logs.

- **Phase 4: Operational Reality (Current)**
    - [x] Integration of real-world tool providers (Web Search, English Dictionary, Crypto Prices).
    - [x] Verification of the end-to-end "Agentic Transaction" loop via `demo_agent.py`.
    - [x] Robust error handling and automated system vitality checks.

## Technical Architecture

The system operates as a managed economic proxy:

1. **Request:** An AI agent sends an authenticated MCP request to the Frappe Gateway.
2. **Authorization:** The Gateway verifies the API credentials, user credit balance, and agent-specific policies.
3. **Settlement:** If authorized, the system deducts internal credits and initiates an x402 settlement to the provider's wallet.
4. **Proxying:** The request is forwarded to the provider's endpoint, and the response is returned to the agent.
5. **Auditing:** All metadata and financial logs are recorded in the Frappe database.

## Prerequisites

- Frappe Framework v15
- Python 3.10+
- Node.js 18+
- Docker (recommended for development)

## Installation

Install the application using the Frappe Bench CLI:

```bash
bench get-app https://github.com/nishanthabimanyu/frappe_x402.git
bench --site [your-site-name] install-app frappe_x402
bench migrate
```

### Optional: EVM Integration
To enable on-chain USDC settlements, install the required EVM dependencies:

```bash
./env/bin/pip install "x402[evm]"
```

## Configuration

### API Authentication
Generate API keys for your AI agents through the **User** DocType in the Frappe Desk. Authenticate requests using the following header:
`Authorization: token [API_KEY]:[API_SECRET]`

### Payment Gateways
Configure Razorpay or Stripe credentials in the system environment variables or through the provided configuration DocTypes to enable fiat credit purchases.

## Development and Testing

The repository includes a `demo_agent.py` script to simulate an AI agent interaction. To run the validation suite:

```bash
bench --site [your-site-name] run-tests --app frappe_x402
```

## Contributing

We welcome contributions that align with the project's architectural standards. Please refer to `CONTRIBUTING.md` for our coding conventions and pull request process.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
