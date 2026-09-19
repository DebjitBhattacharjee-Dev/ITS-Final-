/* Company-wide Executive Dashboard. 100% Live ERPNext Data Integration with Exact Drill-Down. */
(() => {
	let scope = 'all';
	let windowDays = 30;
	let currentDashboardData = null;
	let isLoading = false;

	const box = (title, body, extra = '') => `<section class="panel executive-panel ${extra}"><div class="executive-panel-head"><h2>${title}</h2></div>${body}</section>`;
	const action = (label, key) => `<button class="button" data-executive="${key}">${label} →</button>`;

	async function loadAndRenderDashboard(force = false) {
		const view = $('view');
		if (!view) return;
		if (route !== 'dashboard') return;

		if (!currentDashboardData || force) {
			if (!currentDashboardData) {
				view.innerHTML = `
					<div class="empty" style="padding:80px 20px; text-align:center;">
						<div style="font-size:36px; margin-bottom:16px; animation:spin 1.5s linear infinite;">⏳</div>
						<h2 style="color:#071F4E; font-weight:800;">Connecting to ERPNext Database...</h2>
						<p class="muted">Loading live KPIs, department workload, and priority actions...</p>
					</div>
				`;
			}
			isLoading = true;
			try {
				currentDashboardData = await window.frappeDashboardApi.getDashboardData(scope, dept, windowDays);
			} catch (err) {
				isLoading = false;
				view.innerHTML = `
					<section class="panel pad" style="text-align:center; padding:50px 20px; max-width:600px; margin:40px auto;">
						<h2 style="color:#a04132;">Unable to load live dashboard data</h2>
						<p class="muted">${esc(err.message || 'Error connecting to Frappe backend.')}</p>
						<div style="margin-top:20px;">
							<button class="button primary" onclick="location.reload()">Retry connection</button>
						</div>
					</section>
				`;
				return;
			}
			isLoading = false;
		}

		renderDashboard(currentDashboardData);
	}

	function renderDashboard(data) {
		const view = $('view');
		if (!view || route !== 'dashboard') return;

		const todayStr = data.today || new Date().toISOString().slice(0, 10);
		const currentDeptLabel = dept === 'all' ? 'All departments' : esc((window.DEPARTMENTS && DEPARTMENTS[Number(dept)]) || dept);

		const cards = [
			['Awaiting approval', 'approval', 'Submitted for a decision', data.cards?.approval?.count || 0],
			['Overdue actions', 'overdue', 'Open records past their due date', data.cards?.overdue?.count || 0],
			['Due soon', 'due', `Within the next ${windowDays} days`, data.cards?.due?.count || 0],
			['Returned for correction', 'returned', 'Follow up and resubmit', data.cards?.returned?.count || 0]
		];

		const projectOptions = [
			['all', 'All projects'],
			['TRADING', 'Trading / Normal Projects'],
			['POWERSKID', 'PSS Projects'],
			...(data.projects || []).map(p => [p.id, (p.name || p.id) + (p.customer ? ' · ' + p.customer : '')])
		];

		const priorityItems = data.priority_actions || [];
		const totalRecords = data.review_status?.total_records || 0;
		const totalProjects = data.review_status?.total_projects || (data.projects || []).length;
		const statusList = ['Draft', 'Submitted', 'Returned', 'Approved'];
		const statusColors = ['#a7b4c8', '#3d78b4', '#F18716', '#27836b'];

		const openTotal = (data.review_status?.counts?.Draft || 0) + (data.review_status?.counts?.Submitted || 0) + (data.review_status?.counts?.Returned || 0);

		const commCounts = data.commercial_counts || {};
		const commItems = [
			['RFI', 'rfi'],
			['Inquiries', 'inquiry'],
			['Quotations', 'quotation'],
			['Sales orders', 'order'],
			['Purchase orders', 'purchase'],
			['Line item contracts', 'lineItemContract']
		];

		const finCounts = data.finance_counts || {};
		const finItems = [
			['Tax invoices', 'invoice'],
			['Proforma invoices', 'proforma'],
			['Credit notes', 'creditNote'],
			['Debit notes', 'debitNote'],
			['Payment follow-ups', 'payment'],
			['Supplier invoice reviews', 'supplierInvoice']
		];

		const expiries = data.expiry_watch || [];
		const pss = data.pss || { skids: 0, fatCompleted: 0, ifatCompleted: 0, commissioned: 0, punchOpen: 0, punchOverdue: 0 };
		const pssVisible = scope !== 'TRADING' && ((data.projects || []).some(p => p.project_type === 'POWERSKID') || pss.skids > 0) && dept === 'all';

		const opsCounts = data.operations_counts || {};
		const opsItems = [
			['Employee / manpower records', 'employee'],
			['Timesheets', 'timesheet'],
			['Leave requests', 'leave'],
			['Site access records', 'access'],
			['Daily progress reports', 'dpr'],
			['Shipments', 'shipment']
		];

		view.innerHTML = `
			<section class="executive-hero">
				<div>
					<div class="eyebrow">ITS · COMPANY OVERVIEW</div>
					<h1>Operations dashboard</h1>
					<p>Live ERPNext data — projects, people and commitments across the company.</p>
				</div>
				<div class="executive-date">
					${dateText(todayStr)}
					<small>${currentDeptLabel}</small>
				</div>
			</section>

			<div class="executive-filters">
				<label>Project scope
					<select id="executive-scope">
						${projectOptions.map(([id, name]) => `<option value="${esc(id)}" ${scope === id ? 'selected' : ''}>${esc(name)}</option>`).join('')}
					</select>
				</label>
				<label>Upcoming action / expiry window
					<select id="executive-days">
						${[7, 30, 60, 90].map(n => `<option ${windowDays === n ? 'selected' : ''} value="${n}">Next ${n} days</option>`).join('')}
					</select>
				</label>
				<button class="button" data-executive-refresh>↻ Refresh data</button>
				${btn('Print dashboard', 'print')}
			</div>

			<div class="executive-kpis">
				${cards.map(([label, key, note, count], i) => `
					<button class="executive-kpi ${i === 1 && count > 0 ? 'urgent' : ''}" data-executive="${key}" title="Click to view all ${esc(label)} records">
						<span>${label}</span>
						<strong>${count}</strong>
						<small>${note} ↗</small>
					</button>
				`).join('')}
			</div>

			<div class="executive-layout">
				${box('Priority action list', `
					<p class="muted">Live overdue actions first, followed by upcoming due dates.</p>
					<div class="executive-actions">
						${priorityItems.slice(0, 8).map(r => `
							<div style="cursor:pointer;" onclick="location.hash='#record/${encodeURIComponent(r.doctype)}/${encodeURIComponent(r.id)}'">
								<span>
									<a href="#record/${encodeURIComponent(r.doctype)}/${encodeURIComponent(r.id)}" onclick="event.stopPropagation();">
										<strong>${esc(r.title)}</strong>
									</a>
									<small>${esc(r.owner)} · ${esc(r.project)} · ${esc(r.doctype)}</small>
								</span>
								<span class="${r.is_overdue ? 'late' : ''}">
									${dateText(r.due)}
									<small>${esc(r.status)}</small>
								</span>
							</div>
						`).join('') || '<p>No due actions in the selected window.</p>'}
					</div>
					${action('View overdue records', 'overdue')}
					${action('View upcoming records', 'due')}
				`, 'wide')}

				${box('Record review status', `
					<div class="executive-total">
						<strong>${totalRecords}</strong>
						<span>current live records<br>${totalProjects} projects in scope</span>
					</div>
					${statusList.map((s, i) => {
						const cnt = data.review_status?.counts?.[s] || 0;
						return `
							<div class="executive-bar" style="cursor:pointer;" data-executive="status:${s}" title="Click to view all ${s} records">
								<span>${esc(s)}</span>
								<div><i style="width:${cnt / Math.max(totalRecords, 1) * 100}%; background:${statusColors[i]};"></i></div>
								<strong>${cnt}</strong>
							</div>
						`;
					}).join('')}
					<p class="footer-note">Approval status measures live record review from ERPNext, not physical completion.</p>
				`)}

				${box('Department workload', `
					<p class="muted">Live open records and overdue work by department.</p>
					${(data.workload || []).map(w => `
						<button class="executive-work" data-executive="module:${w.module}" title="Click to view ${esc(w.label)} records">
							<span>${esc(w.label)}</span>
							<span class="executive-track"><i style="width:${w.count / Math.max(openTotal, 1) * 100}%;"></i></span>
							<b>${w.count}</b>
							<small>${w.overdue > 0 ? w.overdue + ' overdue' : 'No overdue'}</small>
						</button>
					`).join('')}
				`, 'wide')}

				${box('Commercial & purchasing', `
					<div class="executive-counts">
						${commItems.map(([label, key]) => `
							<button data-executive="${key}" title="Click to view ${esc(label)} records">
								<span>${label}</span>
								<strong>${commCounts[key] || 0}</strong>
							</button>
						`).join('')}
					</div>
					<p class="footer-note">Current live records, including drafts and approved entries.</p>
				`)}

				${box('Billing & Finance', `
					<div class="executive-counts">
						${finItems.map(([label, key]) => `
							<button data-executive="${key}" title="Click to view ${esc(label)} records">
								<span>${label}</span>
								<strong>${finCounts[key] || 0}</strong>
							</button>
						`).join('')}
					</div>
					<a class="button" href="#list?key=module:8&department=8">Open Billing & Finance →</a>
					<p class="footer-note">Live document counts. Receivables, profit and cash balances require the accounting ledger.</p>
				`)}

				${box('Document expiry watch', `
					<p class="muted">Live records expired and due within ${windowDays} days.</p>
					${expiries.slice(0, 8).map(r => `
						<a class="executive-expiry" href="#record/${encodeURIComponent(r.doctype)}/${encodeURIComponent(r.id)}" title="Click to view document ${esc(r.name)}">
							<span><strong>${esc(r.name)}</strong><small>${esc(r.kind)} · ${esc(r.doctype)}</small></span>
							<span class="${r.is_late ? 'late' : ''}">
								${dateText(r.date)}
								<small>${r.is_late ? 'Expired' : 'Upcoming'}</small>
							</span>
						</a>
					`).join('') || '<p>No recorded expiries in this window.</p>'}
					<p class="footer-note">${expiries.length} matching documents in live ERPNext database.</p>
					<a class="button" href="#list?key=due&days=${windowDays}">View All Upcoming Expiries →</a>
				`, 'wide')}

				${pssVisible ? box('PSS execution', `
					<p class="muted">Dedicated skid execution records for the selected PSS scope.</p>
					<div class="executive-counts">
						${[['Skids', pss.skids, 'skid'], ['FAT completed', pss.fatCompleted, 'fat'], ['IFAT completed', pss.ifatCompleted, 'ifat'], ['Commissioned', pss.commissioned, 'commissioning'], ['Open punch points', pss.punchOpen, 'punch_open'], ['Overdue punch points', pss.punchOverdue, 'punch_overdue']].map(([label, n, key]) => `
							<button data-executive="${key}" title="Click to view ${esc(label)}">
								<span>${label}</span>
								<strong>${n}</strong>
							</button>
						`).join('')}
					</div>
					<a class="button" href="#skids">Open PSS Project Center →</a>
				`) : ''}

				${box('People & site operations', `
					<div class="executive-counts">
						${opsItems.map(([label, key]) => `
							<button data-executive="${key}" title="Click to view ${esc(label)} records">
								<span>${label}</span>
								<strong>${opsCounts[key] || 0}</strong>
							</button>
						`).join('')}
					</div>
					<p class="footer-note">Live record counts from Frappe HR and ERPNext.</p>
				`)}
			</div>

			<section class="panel executive-panel">
				<h2>Quick access</h2>
				<div class="executive-links">
					${[['module/0', 'Commercial'], ['module/10', 'Contracts'], ['module/3', 'Procurement'], ['module/4', 'Logistics'], ['module/8', 'Billing & Finance'], ['module/6', 'HR & Manpower'], ['materials', 'Materials'], ['services', 'Services'], ['approvals', 'Approvals Queue']].map(([path, label]) => `<a class="button" href="#${path}">${label} →</a>`).join('')}
				</div>
			</section>

			<p class="footer-note">All metrics are live queries against Frappe/ERPNext database with strict permission enforcement for current user session.</p>
		`;
	}

	// Register global dashboardPage function
	dashboardPage = function() {
		loadAndRenderDashboard(false);
	};

	// Event listeners for filters and drill-down clicks
	document.addEventListener('change', e => {
		if (e.target.id === 'executive-scope') {
			scope = e.target.value;
			loadAndRenderDashboard(true);
		}
		if (e.target.id === 'executive-days') {
			windowDays = Number(e.target.value);
			loadAndRenderDashboard(true);
		}
	});

	document.addEventListener('click', e => {
		if (e.target.closest('[data-executive-refresh]')) {
			e.preventDefault();
			if (typeof notify === 'function') notify('Refreshing dashboard from Frappe database...');
			loadAndRenderDashboard(true);
			return;
		}

		const el = e.target.closest('[data-executive]');
		if (el) {
			e.preventDefault();
			const key = el.dataset.executive;
			let q = `project=${encodeURIComponent(scope)}&department=${encodeURIComponent(dept)}&days=${encodeURIComponent(windowDays)}`;
			if (key.startsWith('status:')) {
				q += `&status=${encodeURIComponent(key.slice(7))}`;
			} else {
				q += `&key=${encodeURIComponent(key)}`;
			}
			location.hash = `list?${q}`;
		}
	});
})();
