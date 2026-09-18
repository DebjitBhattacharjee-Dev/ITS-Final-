/* ERPNext Single-Record Document Detail Engine with Workflow Approvals and Executive Styling */
(function(window) {
	let currentDoc = null;
	let currentTab = 'details';
	let isEditing = false;
	let editData = null;
	let docErrors = [];

	function esc(s) {
		if (s === null || s === undefined) return '';
		return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
	}

	function statusBadge(status) {
		const s = (status || 'Draft').toString();
		let cls = 'status-draft';
		if (['Pending Review', 'Under review', 'In progress', 'Submitted for review'].includes(s)) cls = 'status-review';
		else if (['Approved', 'Cleared', 'Matched', 'Passed', 'Active', '1'].includes(s)) cls = 'status-approved';
		else if (['Returned', 'Failed', 'Discrepancy'].includes(s)) cls = 'status-returned';
		else if (['Submitted', 'Completed'].includes(s)) cls = 'status-submitted';
		else if (['Cancelled', '2'].includes(s)) cls = 'status-returned';

		return `
			<span class="status-pill-lg ${cls}">
				<span class="status-dot"></span>
				${esc(s)}
			</span>
		`;
	}

	function dateText(d) {
		if (!d) return '—';
		return esc(d.toString().slice(0, 10));
	}

	function money(n, currency = 'AED') {
		const num = Number(n) || 0;
		return 'AED ' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	}

	function parseRouteParam(param) {
		if (!param) return { doctype: null, name: null };
		const parts = param.split('/');
		if (parts.length > 1) {
			return { doctype: decodeURIComponent(parts[0]), name: decodeURIComponent(parts.slice(1).join('/')) };
		}
		return { doctype: null, name: decodeURIComponent(param) };
	}

	async function loadDocument(routeParam) {
		const { doctype, name } = parseRouteParam(routeParam);
		if (!name) return;

		const view = document.getElementById('view');
		view.innerHTML = `
			<div class="empty" style="padding:60px 20px; text-align:center;">
				<div style="font-size:32px; margin-bottom:14px; animation:spin 1.5s linear infinite;">⏳</div>
				<h2 style="color:#002B49; font-weight:800;">Connecting to Frappe MariaDB...</h2>
				<p class="muted">Loading record ${esc(name)} and workflow authorization matrix...</p>
			</div>
		`;

		try {
			const detail = await window.frappeDocApi.getDetail(doctype, name);
			currentDoc = detail;
			isEditing = false;
			editData = null;
			docErrors = [];
			renderDocumentView();
		} catch (err) {
			if (err.status === 403 || err.exc_type === 'PermissionError') {
				view.innerHTML = `
					<div class="empty" style="padding:60px 20px; text-align:center;">
						<h1 style="color:#DC2626; font-size:26px;">403 · Access Restricted</h1>
						<p style="color:#475569; max-width:500px; margin:12px auto;">Your active session does not possess permission to view record <strong>${esc(name)}</strong> in DocType <strong>${esc(doctype || 'ERPNext')}</strong>.</p>
						<div style="margin-top:20px"><a class="button primary" href="#home">Back to workspace</a></div>
					</div>
				`;
			} else {
				view.innerHTML = `
					<div class="empty" style="padding:60px 20px; text-align:center;">
						<h1 style="color:#002B49;">Record Not Found</h1>
						<p style="color:#64748B;">${esc(err.message || 'The requested document could not be retrieved.')}</p>
						<div style="margin-top:20px"><a class="button primary" href="#home">Back to workspace</a></div>
					</div>
				`;
			}
		}
	}

	function renderWorkflowStepper() {
		if (!currentDoc || !currentDoc.workflow_steps) return '';
		const steps = currentDoc.workflow_steps;

		return `
			<div class="doc-workflow-bar">
				<div class="workflow-stepper">
					${steps.map(s => {
						let nodeContent = s.index;
						if (s.state === 'completed') nodeContent = '✓';
						else if (s.state === 'returned') nodeContent = '!';

						return `
							<div class="stepper-step ${s.state}">
								<div class="stepper-node">${nodeContent}</div>
								<div class="stepper-label">${esc(s.label)}</div>
								<div class="stepper-role">${esc(s.role)}</div>
							</div>
						`;
					}).join('')}
				</div>
			</div>
		`;
	}

	function renderDocumentView() {
		if (!currentDoc) return;
		const d = currentDoc;
		const view = document.getElementById('view');
		const act = d.allowed_actions || {};

		// Header Action Buttons based on Workflow & Permissions
		let actionsHtml = '';
		if (isEditing) {
			actionsHtml += `<button class="button" data-doc-action="cancel-edit">Cancel Edit</button>`;
			actionsHtml += `<button class="button primary" data-doc-action="save">Save Changes</button>`;
		} else {
			if (act.can_edit) {
				actionsHtml += `<button class="button" data-doc-action="edit">Edit details</button>`;
			}
			if (act.can_submit_review) {
				actionsHtml += `<button class="button primary" data-doc-action="submit-review">Submit for Review →</button>`;
			}
			if (act.can_approve) {
				actionsHtml += `<button class="button primary" style="background:#16A34A; border-color:#15803D;" data-doc-action="approve">✓ Approve</button>`;
			}
			if (act.can_return) {
				actionsHtml += `<button class="button" style="color:#B91C1C; border-color:#FCA5A5; background:#FEF2F2;" data-doc-action="return">↺ Return for Changes</button>`;
			}
			if (act.can_final_submit) {
				actionsHtml += `<button class="button primary" style="background:#002B49;" data-doc-action="final-submit">Official ERP Submission</button>`;
			}
			if (act.can_cancel) {
				actionsHtml += `<button class="button danger" data-doc-action="cancel">Cancel Document</button>`;
			}
			if (act.can_delete) {
				actionsHtml += `<button class="button" data-doc-action="delete" style="color:#991B1B">Delete</button>`;
			}
			actionsHtml += `<button class="button" data-doc-action="print">Print Document</button>`;
		}

		const titleText = d.title || d.name;
		const subtitleText = `${d.doctype} · Reference ${d.name}`;

		const errorsHtml = docErrors.length ? `
			<div class="error-box" role="alert" style="margin-bottom:20px;">
				<strong>Please check these issues:</strong>
				<ul>${docErrors.map(e => `<li>${esc(e)}</li>`).join('')}</ul>
			</div>
		` : '';

		view.innerHTML = `
			<div class="crumb" style="margin-bottom:12px;">
				<a href="#home">Workspace</a><span>/</span>
				<a href="#module/0">${esc(d.doctype)}</a><span>/</span>
				<strong>${esc(d.name)}</strong>
			</div>

			<div class="doc-hero">
				<div class="doc-hero-main">
					<div class="doc-tag-row">
						<span class="doc-type-tag">${esc(d.doctype)}</span>
						<span class="doc-ref-id">${esc(d.name)}</span>
						${statusBadge(d.status)}
					</div>
					<h1 class="doc-hero-title">${esc(titleText)}</h1>
					<p class="doc-hero-sub">${esc(subtitleText)} · Created by ${esc(d.owner || 'Administrator')} on ${dateText(d.creation)}</p>
				</div>
				<div class="doc-hero-actions">
					${actionsHtml}
				</div>
			</div>

			${renderWorkflowStepper()}

			${errorsHtml}

			<div class="record-layout">
				<div class="main-column" style="flex:1; min-width:0;">
					<div class="tabs" role="tablist" style="margin-bottom:16px;">
						${[
							['details', 'Document Form'],
							['history', `Workflow & Audit History (${d.history.length})`],
							['attachments', `Attachments (${d.attachments.length})`],
							['related', 'Linked Records']
						].map(([t, l]) => `
							<button role="tab" aria-selected="${currentTab === t}" data-doc-tab="${t}" class="${currentTab === t ? 'active' : ''}" ${isEditing && t !== 'details' ? 'disabled' : ''}>${l}</button>
						`).join('')}
					</div>

					<div class="tab-body">
						${renderTabContent()}
					</div>
				</div>

				<div class="side-stack" style="width:320px; shrink:0;">
					<section class="side-panel">
						<div class="next-label">CURRENT WORKFLOW STAGE</div>
						<h3 style="color:#002B49; margin-top:6px;">${getStageTitle(d)}</h3>
						<p style="color:#475569; font-size:13px; line-height:1.45;">${getStageDescription(d)}</p>
						<div class="label" style="margin-top:18px">Active Persona Authority</div>
						<div class="value" style="font-weight:700; color:#005A9C;">${esc(d.persona_label || 'Administrator')}</div>
					</section>

					<section class="side-panel">
						<h3>Approval & Verification</h3>
						<div class="check ${d.status === 'Approved' || d.status === 'Submitted' ? '' : 'pending'}">
							<span class="mark">${d.status === 'Approved' || d.status === 'Submitted' ? '✓' : '○'}</span>
							Department Approval
						</div>
						<div class="check ${d.docstatus === 1 ? '' : 'pending'}">
							<span class="mark">${d.docstatus === 1 ? '✓' : '○'}</span>
							ERP Submission Lock
						</div>
						<div class="check ${d.attachments.length > 0 ? '' : 'pending'}">
							<span class="mark">${d.attachments.length > 0 ? '✓' : '○'}</span>
							Supporting Evidence (${d.attachments.length})
						</div>
					</section>
				</div>
			</div>
		`;

		attachDocEvents();
	}

	function getStageTitle(d) {
		if (d.status === 'Pending Review') return 'Department Verification Required';
		if (d.status === 'Approved') return 'Approved · Ready for Official Submission';
		if (d.status === 'Returned') return 'Returned for Modifications';
		if (d.status === 'Submitted') return 'Locked & Submitted in MariaDB';
		if (d.status === 'Cancelled') return 'Document Cancelled';
		return 'Draft Initiation';
	}

	function getStageDescription(d) {
		if (d.status === 'Pending Review') return 'This document is awaiting review and sign-off by the authorized department lead.';
		if (d.status === 'Approved') return 'Department checks are complete. Proceed with official submission or downstream orders.';
		if (d.status === 'Returned') return 'The reviewer requested revisions. Check audit history comments, update details, and resubmit.';
		if (d.status === 'Submitted') return 'Record is officially logged in ERPNext and protected against tampering.';
		if (d.status === 'Cancelled') return 'This document was cancelled by executive management.';
		return 'Complete all required fields and item lines, then click "Submit for Review".';
	}

	function renderTabContent() {
		if (currentTab === 'details') return renderDetailsTab();
		if (currentTab === 'history') return renderHistoryTab();
		if (currentTab === 'attachments') return renderAttachmentsTab();
		if (currentTab === 'related') return renderRelatedTab();
		return '';
	}

	function renderDetailsTab() {
		if (isEditing) return renderEditDetailsForm();

		const d = currentDoc;
		const sec = d.sections || {};

		function renderSectionFields(fields) {
			if (!fields || !fields.length) return '<p class="muted">No fields defined.</p>';
			return `
				<div class="doc-fields-grid">
					${fields.map(fm => {
						const val = d.fields[fm.fieldname];
						let displayVal = val;
						if (fm.fieldtype === 'Date' || fm.fieldtype === 'Datetime') {
							displayVal = dateText(val);
						} else if (['Currency', 'Float'].includes(fm.fieldtype)) {
							displayVal = val !== null && val !== undefined ? money(val) : '—';
						} else if (fm.fieldtype === 'Check') {
							displayVal = val ? 'Yes' : 'No';
						} else if (fm.fieldtype === 'Link') {
							displayVal = val ? `<a href="#record/${encodeURIComponent(fm.options)}/${encodeURIComponent(val)}">${esc(val)} →</a>` : '<span class="muted">Not set</span>';
						} else if (val === null || val === undefined || val === '') {
							displayVal = '<span class="muted">—</span>';
						} else {
							displayVal = esc(val);
						}

						return `
							<div class="doc-field-item">
								<div class="doc-field-label">${esc(fm.label)}</div>
								<div class="doc-field-value">${displayVal}</div>
							</div>
						`;
					}).join('')}
				</div>
			`;
		}

		// Line Items Rendering
		let linesHtml = renderLineItemsRead();

		return `
			<div class="doc-section-card">
				<h3 class="section-header">General Information</h3>
				${renderSectionFields(sec.general)}
			</div>

			<div class="doc-section-card">
				<h3 class="section-header">Stakeholders & Responsibility</h3>
				${renderSectionFields(sec.stakeholders)}
			</div>

			<div class="doc-section-card">
				<h3 class="section-header">Schedule & Logistics</h3>
				${renderSectionFields(sec.schedule)}
			</div>

			${sec.other && sec.other.length ? `
				<div class="doc-section-card">
					<h3 class="section-header">Additional Details</h3>
					${renderSectionFields(sec.other)}
				</div>
			` : ''}

			${linesHtml}
		`;
	}

	function renderLineItemsRead() {
		const d = currentDoc;
		let lines = [];
		let subtotal = 0;
		let taxRate = 5;

		const pData = d.prototype_data || {};
		if (pData.lines && pData.lines.length) {
			lines = pData.lines.map((l, i) => {
				const q = Number(l.qty) || 1;
				const r = Number(l.rate) || 0;
				const amt = q * r;
				subtotal += amt;
				return { idx: i + 1, code: l.code || '—', partNo: l.partNo || '—', desc: l.description || '', qty: q, unit: l.unit || 'Nos', rate: r, amt };
			});
			taxRate = Number(pData.taxRate) || 0;
		} else if (d.table_fields && d.table_fields.length) {
			for (const tf of d.table_fields) {
				const rows = d.tables[tf.fieldname] || [];
				if (rows.length) {
					lines = rows.map((r, i) => {
						const q = Number(r.qty) || 1;
						const rt = Number(r.rate || r.unit_price) || 0;
						const amt = Number(r.amount) || (q * rt);
						subtotal += amt;
						return { idx: i + 1, code: r.item_code || r.code || '—', partNo: r.part_no || '—', desc: r.item_name || r.description || '', qty: q, unit: r.uom || r.unit || 'Nos', rate: rt, amt };
					});
					break;
				}
			}
		}

		if (!lines.length) return '';

		const taxAmount = subtotal * (taxRate / 100);
		const grandTotal = subtotal + taxAmount;

		return `
			<div class="doc-section-card">
				<h3 class="section-header">Items & Commercial Scope</h3>
				<div style="overflow-x:auto;">
					<table class="doc-line-table">
						<thead>
							<tr>
								<th style="width:40px">#</th>
								<th style="width:130px">Material Code</th>
								<th>Description</th>
								<th class="num" style="width:70px">Qty</th>
								<th style="width:60px">Unit</th>
								<th class="num" style="width:120px">Unit Price</th>
								<th class="num" style="width:130px">Total Amount</th>
							</tr>
						</thead>
						<tbody>
							${lines.map(l => `
								<tr>
									<td style="text-align:center;">${l.idx}</td>
									<td style="font-family:monospace; font-weight:700; color:#002B49;">${esc(l.code)}</td>
									<td>${esc(l.desc)}</td>
									<td class="num">${l.qty}</td>
									<td>${esc(l.unit)}</td>
									<td class="num">${money(l.rate)}</td>
									<td class="num" style="font-weight:700; color:#002B49;">${money(l.amt)}</td>
								</tr>
							`).join('')}
						</tbody>
					</table>
				</div>

				<div class="doc-financial-summary">
					<div class="doc-sum-row">
						<span>Subtotal (Net)</span>
						<strong>${money(subtotal)}</strong>
					</div>
					<div class="doc-sum-row">
						<span>VAT (${taxRate}%)</span>
						<strong>${money(taxAmount)}</strong>
					</div>
					<div class="doc-sum-row grand">
						<span>Grand Total</span>
						<span>${money(grandTotal)}</span>
					</div>
				</div>
			</div>
		`;
	}

	function renderEditDetailsForm() {
		const d = currentDoc;
		if (!editData) {
			editData = {
				fields: { ...d.fields },
				tables: JSON.parse(JSON.stringify(d.tables || {})),
				prototype_data: JSON.parse(JSON.stringify(d.prototype_data || {}))
			};
		}

		function renderEditFields(fields) {
			return `
				<div class="doc-fields-grid">
					${fields.map(fm => {
						const val = editData.fields[fm.fieldname] !== undefined ? editData.fields[fm.fieldname] : '';
						const name = `field:${fm.fieldname}`;
						let inputHtml = '';

						if (fm.fieldtype === 'Select' && fm.options) {
							const opts = fm.options.split('\n').filter(Boolean);
							inputHtml = `<select name="${name}">${opts.map(o => `<option value="${esc(o)}" ${o == val ? 'selected' : ''}>${esc(o)}</option>`).join('')}</select>`;
						} else if (fm.fieldtype === 'Small Text' || fm.fieldtype === 'Long Text') {
							inputHtml = `<textarea name="${name}">${esc(val)}</textarea>`;
						} else if (fm.fieldtype === 'Date') {
							inputHtml = `<input type="date" name="${name}" value="${esc(val)}">`;
						} else if (['Int', 'Float', 'Currency'].includes(fm.fieldtype)) {
							inputHtml = `<input type="number" step="any" name="${name}" value="${esc(val)}">`;
						} else if (fm.fieldtype === 'Check') {
							inputHtml = `<input type="checkbox" name="${name}" ${val ? 'checked' : ''}>`;
						} else {
							inputHtml = `<input type="text" name="${name}" value="${esc(val)}">`;
						}

						return `
							<div class="doc-field-item doc-input-wrap">
								<label class="doc-field-label">
									${esc(fm.label)} ${fm.reqd ? '<span style="color:#DC2626">*</span>' : ''}
								</label>
								${inputHtml}
							</div>
						`;
					}).join('')}
				</div>
			`;
		}

		// Editable Child Tables
		let childTableHtml = renderEditableLines();

		return `
			<form id="doc-edit-form" novalidate>
				<div class="doc-section-card">
					<h3 class="section-header">General Information</h3>
					${renderEditFields(d.sections.general)}
				</div>

				<div class="doc-section-card">
					<h3 class="section-header">Stakeholders & Responsibility</h3>
					${renderEditFields(d.sections.stakeholders)}
				</div>

				<div class="doc-section-card">
					<h3 class="section-header">Schedule & Logistics</h3>
					${renderEditFields(d.sections.schedule)}
				</div>

				${childTableHtml}

				<div class="form-actions" style="margin-top:24px; display:flex; gap:12px; justify-content:flex-end;">
					<button type="button" class="button" data-doc-action="cancel-edit">Cancel</button>
					<button type="button" class="button primary" data-doc-action="save">Save Changes</button>
				</div>
			</form>
		`;
	}

	function renderEditableLines() {
		const pData = editData.prototype_data;
		const lines = pData.lines || [];

		return `
			<div class="doc-section-card">
				<div class="split" style="margin-bottom:12px;">
					<h3 class="section-header" style="margin:0; border:none;">Line Items & Commercial Scope</h3>
					<button type="button" class="button small" data-doc-action="add-line">+ Add Line Item</button>
				</div>
				<div style="overflow-x:auto;">
					<table class="doc-line-table">
						<thead>
							<tr>
								<th style="width:30px">#</th>
								<th style="width:130px">Material Code</th>
								<th>Description</th>
								<th class="num" style="width:80px">Qty</th>
								<th style="width:70px">Unit</th>
								<th class="num" style="width:110px">Rate (AED)</th>
								<th class="num" style="width:120px">Total Amount</th>
								<th style="width:40px"></th>
							</tr>
						</thead>
						<tbody>
							${lines.map((l, i) => `
								<tr>
									<td style="text-align:center;">${i + 1}</td>
									<td><input name="line:${i}:code" value="${esc(l.code || '')}" placeholder="Code"></td>
									<td><input name="line:${i}:description" value="${esc(l.description || '')}" placeholder="Item description"></td>
									<td><input type="number" step="any" class="calc-trigger" name="line:${i}:qty" value="${l.qty || 1}"></td>
									<td><input name="line:${i}:unit" value="${esc(l.unit || 'Nos')}"></td>
									<td><input type="number" step="any" class="calc-trigger" name="line:${i}:rate" value="${l.rate || 0}"></td>
									<td class="num" id="line-amount-${i}" style="font-weight:700; color:#002B49;">${money((l.qty || 1) * (l.rate || 0))}</td>
									<td style="text-align:center;">
										<button type="button" class="icon-button" data-doc-action="remove-line" data-index="${i}" style="color:#DC2626;">×</button>
									</td>
								</tr>
							`).join('')}
						</tbody>
					</table>
				</div>
			</div>
		`;
	}

	function renderHistoryTab() {
		const d = currentDoc;
		return `
			<div class="doc-section-card">
				<h3 class="section-header">Workflow & Activity Audit Trail</h3>
				<p class="muted" style="margin-bottom:16px;">Complete timestamped audit log of all creations, reviews, returns, approvals, and comments.</p>
				<div class="timeline">
					${d.history.map(h => `
						<div class="event" style="margin-bottom:14px;">
							<div style="font-size:13px; font-weight:700; color:#002B49;">${esc(h.action)}</div>
							<small style="color:#64748B;">By: ${esc(h.actor)} · ${dateText(h.time)}</small>
						</div>
					`).join('')}
				</div>
			</div>
		`;
	}

	function renderAttachmentsTab() {
		const d = currentDoc;
		return `
			<div class="doc-section-card">
				<div class="split" style="margin-bottom:16px;">
					<div>
						<h3 class="section-header" style="margin:0; border:none;">Attached Documents & Evidence</h3>
						<p class="muted" style="margin:4px 0 0 0;">Attached files stored securely in Frappe MariaDB.</p>
					</div>
					<label class="button primary" style="cursor:pointer">
						+ Upload Attachment
						<input type="file" id="doc-file-upload-input" style="display:none">
					</label>
				</div>
				<div style="overflow-x:auto;">
					<table class="doc-line-table">
						<thead>
							<tr>
								<th>File Name</th>
								<th style="width:100px">File Size</th>
								<th style="width:140px">Upload Date</th>
								<th style="width:110px">Action</th>
							</tr>
						</thead>
						<tbody>
							${d.attachments.map(f => `
								<tr>
									<td><strong>${esc(f.name)}</strong></td>
									<td>${Math.round((f.size || 0) / 1024)} KB</td>
									<td>${dateText(f.created)}</td>
									<td><a class="button small" href="${esc(f.url)}" target="_blank">Download</a></td>
								</tr>
							`).join('') || '<tr><td colspan="4" class="muted" style="text-align:center; padding:20px;">No attachments linked to this document yet.</td></tr>'}
						</tbody>
					</table>
				</div>
			</div>
		`;
	}

	function renderRelatedTab() {
		const d = currentDoc;
		const links = [];
		for (const fm of d.fields_meta) {
			if (fm.fieldtype === 'Link' && d.fields[fm.fieldname]) {
				links.push({ label: fm.label, doctype: fm.options, name: d.fields[fm.fieldname] });
			}
		}

		return `
			<div class="doc-section-card">
				<h3 class="section-header">Connected Flow & Linked Records</h3>
				<div class="quick-grid">
					${links.map(l => `
						<a class="quick" href="#record/${encodeURIComponent(l.doctype)}/${encodeURIComponent(l.name)}" style="text-decoration:none;">
							<span class="plus">↗</span>
							${esc(l.label)}: ${esc(l.name)}
							<small>${esc(l.doctype)}</small>
						</a>
					`).join('') || '<p class="muted">No direct linked documents found in fields.</p>'}
				</div>
			</div>
		`;
	}

	function collectFormData() {
		if (!editData) return;
		const form = document.getElementById('doc-edit-form');
		if (!form) return;

		const formData = new FormData(form);
		for (const [key, val] of formData.entries()) {
			if (key.startsWith('field:')) {
				const fieldname = key.slice(6);
				editData.fields[fieldname] = val;
			} else if (key.startsWith('line:')) {
				const [, idxStr, prop] = key.split(':');
				const idx = Number(idxStr);
				if (editData.prototype_data.lines && editData.prototype_data.lines[idx]) {
					editData.prototype_data.lines[idx][prop] = ['qty', 'rate'].includes(prop) ? Number(val) : val;
				}
			}
		}
	}

	function showReturnDialog() {
		const dialog = document.getElementById('dialog');
		const dialogBody = document.getElementById('dialog-body');
		dialogBody.innerHTML = `
			<div class="return-modal-box">
				<div class="eyebrow" style="color:#DC2626;">WORKFLOW REVISION</div>
				<h3>Return for Changes</h3>
				<p>Please enter the specific feedback or required corrections for the requester before resubmitting.</p>
				<form id="doc-return-modal-form">
					<textarea name="return_reason" required placeholder="e.g. Please update material unit price and attach client SES certificate..."></textarea>
					<div class="form-actions" style="display:flex; justify-content:flex-end; gap:10px;">
						<button type="button" class="button" onclick="document.getElementById('dialog').close()">Cancel</button>
						<button type="submit" class="button danger">Return Record</button>
					</div>
				</form>
			</div>
		`;
		dialog.showModal();

		document.getElementById('doc-return-modal-form').onsubmit = async (e) => {
			e.preventDefault();
			const reason = e.target.return_reason.value.trim();
			if (!reason) return;
			dialog.close();

			try {
				const updated = await window.frappeDocApi.transitionWorkflow(currentDoc.doctype, currentDoc.name, 'return', reason);
				currentDoc = updated;
				if (typeof notify === 'function') notify('Document returned for changes.');
				renderDocumentView();
			} catch (err) {
				alert(err.message);
			}
		};
	}

	function attachDocEvents() {
		const view = document.getElementById('view');

		// Tab Switching
		view.querySelectorAll('[data-doc-tab]').forEach(btn => {
			btn.onclick = () => {
				currentTab = btn.dataset.docTab;
				renderDocumentView();
			};
		});

		// Live Calculation on Input
		view.querySelectorAll('.calc-trigger').forEach(input => {
			input.oninput = () => {
				collectFormData();
				editData.prototype_data.lines.forEach((l, i) => {
					const el = document.getElementById(`line-amount-${i}`);
					if (el) el.textContent = money((Number(l.qty) || 1) * (Number(l.rate) || 0));
				});
			};
		});

		// Action Handlers
		view.querySelectorAll('[data-doc-action]').forEach(btn => {
			btn.onclick = async (e) => {
				e.preventDefault();
				const action = btn.dataset.docAction;

				if (action === 'edit') {
					isEditing = true;
					editData = {
						fields: { ...currentDoc.fields },
						tables: JSON.parse(JSON.stringify(currentDoc.tables || {})),
						prototype_data: JSON.parse(JSON.stringify(currentDoc.prototype_data || {}))
					};
					docErrors = [];
					renderDocumentView();
				} else if (action === 'cancel-edit') {
					isEditing = false;
					editData = null;
					docErrors = [];
					renderDocumentView();
				} else if (action === 'save') {
					collectFormData();
					try {
						btn.disabled = true;
						const updated = await window.frappeDocApi.saveDetail(currentDoc.doctype, currentDoc.name, editData);
						currentDoc = updated;
						isEditing = false;
						editData = null;
						docErrors = [];
						if (typeof notify === 'function') notify('Changes saved to MariaDB.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						docErrors = [err.message];
						renderDocumentView();
					}
				} else if (action === 'submit-review') {
					try {
						btn.disabled = true;
						const updated = await window.frappeDocApi.transitionWorkflow(currentDoc.doctype, currentDoc.name, 'submit_review', 'Submitted for review');
						currentDoc = updated;
						if (typeof notify === 'function') notify('Submitted for review.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						alert(err.message);
					}
				} else if (action === 'approve') {
					if (!confirm(`Confirm approval for ${currentDoc.name}?`)) return;
					try {
						btn.disabled = true;
						const updated = await window.frappeDocApi.transitionWorkflow(currentDoc.doctype, currentDoc.name, 'approve', 'Approved');
						currentDoc = updated;
						if (typeof notify === 'function') notify('Document approved.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						alert(err.message);
					}
				} else if (action === 'return') {
					showReturnDialog();
				} else if (action === 'final-submit') {
					if (!confirm(`Submit and lock ${currentDoc.name} in ERPNext?`)) return;
					try {
						btn.disabled = true;
						const updated = await window.frappeDocApi.transitionWorkflow(currentDoc.doctype, currentDoc.name, 'final_submit', 'Official ERP Submission');
						currentDoc = updated;
						if (typeof notify === 'function') notify('Document submitted & locked.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						alert(err.message);
					}
				} else if (action === 'cancel') {
					if (!confirm(`Cancel ${currentDoc.name}?`)) return;
					try {
						btn.disabled = true;
						const updated = await window.frappeDocApi.transitionWorkflow(currentDoc.doctype, currentDoc.name, 'cancel', 'Document Cancelled');
						currentDoc = updated;
						if (typeof notify === 'function') notify('Document cancelled.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						alert(err.message);
					}
				} else if (action === 'delete') {
					if (!confirm(`Permanently delete ${currentDoc.name}?`)) return;
					try {
						btn.disabled = true;
						await window.frappeDocApi.deleteDetail(currentDoc.doctype, currentDoc.name);
						if (typeof notify === 'function') notify('Document deleted.');
						window.location.hash = '#home';
					} catch (err) {
						btn.disabled = false;
						alert(err.message);
					}
				} else if (action === 'print') {
					try {
						const printData = await window.frappeDocApi.getPrint(currentDoc.doctype, currentDoc.name);
						const w = window.open('', '_blank');
						w.document.write(printData.html);
						w.document.close();
						w.focus();
					} catch (err) {
						alert(err.message);
					}
				} else if (action === 'add-line') {
					collectFormData();
					if (!editData.prototype_data.lines) editData.prototype_data.lines = [];
					editData.prototype_data.lines.push({ code: '', description: '', qty: 1, unit: 'Nos', rate: 0 });
					renderDocumentView();
				} else if (action === 'remove-line') {
					collectFormData();
					const idx = Number(btn.dataset.index);
					if (editData.prototype_data.lines) {
						editData.prototype_data.lines.splice(idx, 1);
					}
					renderDocumentView();
				}
			};
		});

		// File Upload
		const fileInput = document.getElementById('doc-file-upload-input');
		if (fileInput) {
			fileInput.onchange = async () => {
				const file = fileInput.files[0];
				if (!file) return;
				const reader = new FileReader();
				reader.onload = async () => {
					const base64Data = reader.result.split(',')[1];
					try {
						await fetch('/api/attachments', {
							method: 'POST',
							headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': window.csrf_token || '' },
							body: JSON.stringify({
								projectId: currentDoc.name,
								recordId: currentDoc.name,
								name: file.name,
								base64_data: base64Data
							})
						});
						if (typeof notify === 'function') notify('File attached successfully.');
						loadDocument(`${currentDoc.doctype}/${currentDoc.name}`);
					} catch (err) {
						alert('File upload failed: ' + err.message);
					}
				};
				reader.readAsDataURL(file);
			};
		}
	}

	window.erpDocumentEngine = {
		loadDocument,
		renderDocumentView
	};
})(window);
