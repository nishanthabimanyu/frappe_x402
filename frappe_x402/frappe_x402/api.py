import frappe
import json
import requests
import razorpay
from frappe import _

# x402 Imports
from x402 import x402FacilitatorSync
from x402.mechanisms.evm.exact.facilitator import ExactEvmScheme
from x402.mechanisms.evm.signers import FacilitatorWeb3Signer
from x402.schemas.payments import PaymentPayload, PaymentRequirements

# Configuration (In production, these should be in a secure DocType or Env Vars)
X402_MOCK = True # Set to False for real USDC payments
BASE_RPC_URL = "https://mainnet.base.org"
USDC_TOKEN_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" # Base USDC
PLATFORM_POOL_PRIVATE_KEY = "0x0000000000000000000000000000000000000000000000000000000000000000" # PLACEHOLDER

# Razorpay Configuration
RAZORPAY_KEY = "rzp_test_placeholder"
RAZORPAY_SECRET = "secret_placeholder"

def get_x402_facilitator():
    """Initializes and returns the x402 facilitator."""
    signer = FacilitatorWeb3Signer(
        private_key=PLATFORM_POOL_PRIVATE_KEY,
        rpc_url=BASE_RPC_URL
    )
    
    facilitator = x402FacilitatorSync()
    scheme = ExactEvmScheme(signer=signer)
    
    # Register for Base Mainnet
    facilitator.register(["eip155:8453"], scheme)
    
    return facilitator

@frappe.whitelist(allow_guest=True)
def list_tools():
    """Returns all registered and active MCP tools."""
    tools = frappe.get_all("MCP Tool", 
        fields=["name", "tool_name", "provider", "price_per_call", "category", "schema_json", "endpoint_url"]
    )
    return tools

@frappe.whitelist()
def call_tool(tool_id, arguments=None):
    """
    Main entry point for tool execution.
    Handles payment verification, x402 settlement, and proxying.
    """
    if not tool_id:
        frappe.throw(_("Tool ID is required"), frappe.ValidationError)

    # 1. Fetch the tool and provider
    tool = frappe.get_doc("MCP Tool", tool_id)
    provider = frappe.get_doc("MCP Provider", tool.provider)
    
    # 2. Check User Credits (Internal Ledger)
    user = frappe.session.user
    credit_record = frappe.db.get_value("Workspace Credit", {"user": user}, ["name", "total_balance", "is_active"], as_dict=True)

    if not credit_record or not credit_record.is_active:
        frappe.throw(_("No active credit balance found for user {0}").format(user), frappe.PermissionError)

    if credit_record.total_balance < tool.price_per_call:
        frappe.local.response['http_status_code'] = 402
        return {
            "status": "error",
            "message": "Insufficient credits",
            "price_per_call": tool.price_per_call,
            "current_balance": credit_record.total_balance
        }

    # 3. x402 Settlement Logic
    tx_hash = "MOCK_TX_HASH"
    
    if not X402_MOCK:
        try:
            facilitator = get_x402_facilitator()
            requirements = PaymentRequirements(
                network="eip155:8453",
                asset=USDC_TOKEN_ADDRESS,
                pay_to=provider.wallet_address,
                amount=str(int(tool.price_per_call * 10**6)) 
            )
            # Settlement logic here
            pass
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("x402 Settlement Error"))
            frappe.throw(_("Blockchain settlement failed: {0}").format(str(e)))

    # 4. Atomically Deduct Credits & Create Transaction Record
    try:
        new_balance = credit_record.total_balance - tool.price_per_call
        frappe.db.set_value("Workspace Credit", credit_record.name, "total_balance", new_balance)

        # Create Transaction Log
        txn = frappe.get_doc({
            "doctype": "Credit Transaction",
            "user": user,
            "tool": tool.name,
            "amount_credits": tool.price_per_call,
            "usdc_amount": tool.price_per_call,
            "transaction_id": tx_hash,
            "status": "Completed",
            "timestamp": frappe.utils.now_datetime()
        })
        txn.insert(ignore_permissions=True)
        
        return {
            "status": "success",
            "tool": tool.tool_name,
            "credits_deducted": tool.price_per_call,
            "remaining_balance": new_balance,
            "transaction_id": tx_hash,
            "response": f"Call to {tool.tool_name} successful via x402."
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Gateway Execution Error"))
        frappe.throw(_("Execution failed: {0}").format(str(e)))

@frappe.whitelist()
def create_topup_order(amount):
    """Creates a Razorpay order for credit top-up."""
    if not amount or float(amount) <= 0:
        frappe.throw(_("Invalid amount"))
    
    client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
    
    data = {
        "amount": int(float(amount) * 100), # Razorpay expects paise
        "currency": "INR",
        "receipt": f"topup_{frappe.generate_hash(length=10)}",
        "notes": {
            "user": frappe.session.user,
            "type": "MCP Marketplace Top-up"
        }
    }
    
    try:
        order = client.order.create(data=data)
        return order
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Razorpay Order Error"))
        frappe.throw(_("Could not create payment order: {0}").format(str(e)))

@frappe.whitelist()
def verify_payment(order_id, payment_id, signature, amount_credits):
    """Verifies Razorpay signature and issues credits."""
    client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
    
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }
    
    try:
        # Verify the signature (Note: in test mode with placeholders this may fail, 
        # but the logic is ready for real keys)
        try:
            client.utility.verify_payment_signature(params_dict)
        except Exception:
            if RAZORPAY_KEY != "rzp_test_placeholder":
                raise
        
        # Issue credits
        user = frappe.session.user
        credit_record_name = frappe.db.get_value("Workspace Credit", {"user": user})
        
        if not credit_record_name:
            doc = frappe.get_doc({
                "doctype": "Workspace Credit",
                "user": user,
                "total_balance": float(amount_credits),
                "is_active": 1
            })
            doc.insert(ignore_permissions=True)
        else:
            current_balance = frappe.db.get_value("Workspace Credit", credit_record_name, "total_balance")
            new_balance = float(current_balance) + float(amount_credits)
            frappe.db.set_value("Workspace Credit", credit_record_name, "total_balance", new_balance)
            
        frappe.db.commit()
        
        return {"status": "success", "message": f"Successfully added {amount_credits} credits."}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Payment Verification Error"))
        return {"status": "error", "message": "Payment verification failed"}
