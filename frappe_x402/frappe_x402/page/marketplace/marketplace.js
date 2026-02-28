frappe.pages['marketplace'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'AI Tool Marketplace',
		single_column: true
	});

	page.main.html(`
		<div class="marketplace-header" style="margin-bottom: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
			<div>
				<h3>Available Tools</h3>
				<p class="text-muted">Discover and call MCP tools instantly.</p>
			</div>
			<div style="display: flex; align-items: center; gap: 20px;">
				<button class="btn btn-primary" id="topup-btn">Top Up Credits</button>
				<div id="user-balance" style="text-align: right; background: #fff; padding: 10px 20px; border: 1px solid #d1d8dd; border-radius: 6px;">
					<div class="text-muted" style="font-size: 12px;">Your Balance</div>
					<div id="balance-amount" style="font-size: 20px; font-weight: bold; color: #2ecc71;">0.00 Credits</div>
				</div>
			</div>
		</div>
		<div id="tools-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">
			<!-- Tools will be injected here -->
		</div>
	`);

	// Initial Load
	update_balance();
	load_tools();

	// Top Up Logic
	$('#topup-btn').on('click', function() {
		let d = new frappe.ui.Dialog({
			title: 'Top Up Credits',
			fields: [
				{
					label: 'Amount (INR)',
					fieldname: 'amount',
					fieldtype: 'Currency',
					reqd: 1,
					default: 500
				}
			],
			primary_action_label: 'Proceed to Pay',
			primary_action(values) {
				d.hide();
				top_up_balance(values.amount);
			}
		});
		d.show();
	});

	function top_up_balance(amount) {
		frappe.call({
			method: 'frappe_x402.frappe_x402.api.create_topup_order',
			args: { amount: amount },
			callback: function(r) {
				if (r.message) {
					var options = {
						"key": "rzp_test_placeholder",
						"amount": r.message.amount,
						"currency": "INR",
						"name": "MCP Marketplace",
						"description": "Credit Top-up",
						"order_id": r.message.id,
						"handler": function (response){
							verify_payment(response, amount);
						},
						"prefill": {
							"email": frappe.session.user_email
						},
						"theme": {
							"color": "#3399cc"
						}
					};
					
					// Load Razorpay Script dynamically if not loaded
					if (typeof Razorpay === 'undefined') {
						$.getScript('https://checkout.razorpay.com/v1/checkout.js', function() {
							var rzp1 = new Razorpay(options);
							rzp1.open();
						});
					} else {
						var rzp1 = new Razorpay(options);
						rzp1.open();
					}
				}
			}
		});
	}

	function verify_payment(response, amount) {
		frappe.call({
			method: 'frappe_x402.frappe_x402.api.verify_payment',
			args: {
				order_id: response.razorpay_order_id,
				payment_id: response.razorpay_payment_id,
				signature: response.razorpay_signature,
				amount_credits: amount
			},
			callback: function(r) {
				if (r.message && r.message.status === 'success') {
					frappe.show_alert({message: r.message.message, indicator: 'green'});
					update_balance();
				}
			}
		});
	}

	function update_balance() {
		frappe.db.get_value('Workspace Credit', {user: frappe.session.user}, 'total_balance')
			.then(r => {
				if (r.message && r.message.total_balance !== undefined) {
					$('#balance-amount').text(r.message.total_balance.toFixed(2) + ' Credits');
				}
			});
	}

	function load_tools() {
		frappe.call({
			method: 'frappe_x402.frappe_x402.api.list_tools',
			callback: function(r) {
				if (r.message) {
					var container = $('#tools-grid');
					container.empty();
					r.message.forEach(tool => {
						var card = $(`
							<div class="tool-card" style="border: 1px solid #d1d8dd; border-radius: 8px; padding: 20px; background: #fff; transition: transform 0.2s;">
								<div style="display: flex; justify-content: space-between; align-items: start;">
									<span class="label label-blue" style="font-size: 10px; margin-bottom: 10px;">${tool.category || 'Tool'}</span>
									<span style="font-weight: bold; color: #34495e;">${tool.price_per_call} Credits/Call</span>
								</div>
								<h4 style="margin: 10px 0;">${tool.tool_name}</h4>
								<p class="text-muted" style="font-size: 13px; height: 40px; overflow: hidden;">${tool.provider_name || 'by x402 AI Labs'}</p>
								<button class="btn btn-primary btn-block btn-sm call-btn" data-id="${tool.name}">Call Tool</button>
							</div>
						`);
						
						card.find('.call-btn').on('click', function() {
							call_tool(tool.name, tool.tool_name);
						});
						
						container.append(card);
					});
				}
			}
		});
	}

	function call_tool(tool_id, tool_name) {
		frappe.confirm(`Call ${tool_name}? This will deduct credits from your balance.`, function() {
			frappe.call({
				method: 'frappe_x402.frappe_x402.api.call_tool',
				args: { tool_id: tool_id },
				callback: function(r) {
					if (r.message && r.message.status === 'success') {
						frappe.show_alert({message: r.message.response, indicator: 'green'});
						update_balance();
					} else if (r.message && r.message.status === 'error') {
						frappe.msgprint({
							title: 'Insufficient Balance',
							message: 'Please top up your credits to call this tool.',
							indicator: 'red'
						});
					}
				}
			});
		});
	}
}
