/* ERPNext Single-Record Document Detail Engine for /review Portal */
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

	function badge(status) {
		const s = (status || 'Draft').toString();
		let cls = 'badge';
		if (['Submitted', 'Under review', 'In progress'].includes(s)) cls += ' status-submitted';
		else if (['Approved', 'Cleared', 'Matched', 'Passed', 'Active', '1'].includes(s)) cls += ' status-approved';
		else if (['Returned', 'Failed', 'Cancelled', '2', 'Discrepancy'].includes(s)) cls += ' status-returned';
		return `<span class="${cls}">${esc(s)}</span>`;
	}

	function dateText(d) {
		if (!d) return '—';
		return esc(d.toString().slice(0, 10));
	}

	function money(n, currency = 'AED') {
		return new Intl.NumberFormat('en-AE', { style: 'currency', currency: currency || 'AED', maximumFractionDigits: 2 }).format(Number(n) || 0);
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
			<div class="empty" style="padding:60px 20px;">
				<div style="font-size:24px; margin-bottom:12px;">⏳</div>
				<h2>Loading ERPNext Document...</h2>
				<p class="muted">Fetching record ${esc(name)} and permissions from MariaDB...</p>
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
					<div class="empty" style="padding:60px 20px;">
						<h1 style="color:#a04132">403 · Permission Denied</h1>
						<p>Your Frappe user session does not have permission to view record <strong>${esc(name)}</strong>.</p>
						<div style="margin-top:20px"><a class="button primary" href="#home">Back to workspace</a></div>
					</div>
				`;
			} else {
				view.innerHTML = `
					<div class="empty" style="padding:60px 20px;">
						<h1>Record Not Found</h1>
						<p>${esc(err.message || 'The requested document could not be retrieved.')}</p>
						<div style="margin-top:20px"><a class="button primary" href="#home">Back to workspace</a></div>
					</div>
				`;
			}
		}
	}

	function renderDocumentView() {
		if (!currentDoc) return;
		const d = currentDoc;
		const view = document.getElementById('view');

		// Header Action Buttons based on Frappe permissions
		let actions = '';
		if (isEditing) {
			actions += `<button class="button" data-doc-action="cancel-edit">Cancel Edit</button>`;
			actions += `<button class="button primary" data-doc-action="save">Save Changes</button>`;
		} else {
			if (d.permissions.write && d.docstatus === 0) {
				actions += `<button class="button" data-doc-action="edit">Edit details</button>`;
			}
			if (d.permissions.submit && d.docstatus === 0) {
				actions += `<button class="button primary" data-doc-action="submit">Submit for review</button>`;
			}
			if (d.permissions.cancel && d.docstatus === 1) {
				actions += `<button class="button danger" data-doc-action="cancel">Cancel Document</button>`;
			}
			if (d.permissions.delete) {
				actions += `<button class="button" data-doc-action="delete" style="color:#a04132">Delete</button>`;
			}
			if (d.permissions.read) {
				actions += `<button class="button" data-doc-action="print">Print</button>`;
			}
		}

		const moduleLabel = d.doctype;
		const titleText = d.title || d.name;
		const subtitleText = `${d.doctype} · ${d.name}`;

		const errorsHtml = docErrors.length ? `
			<div class="error-box" role="alert">
				<strong>Please check these issues before saving:</strong>
				<ul>${docErrors.map(e => `<li>${esc(e)}</li>`).join('')}</ul>
			</div>
		` : '';

		view.innerHTML = `
			<div class="crumb">
				<a href="#home">Workspace</a><span>/</span>
				<span>${esc(moduleLabel)}</span><span>/</span>
				${esc(d.name)}
			</div>
			<div class="page-heading">
				<div class="eyebrow">${esc(d.doctype.toUpperCase())} · ${esc(d.name)}</div>
				<h1>${esc(titleText)}</h1>
				<p class="subtitle">${esc(subtitleText)} · DocStatus: ${d.docstatus}</p>
				<div class="actions">${actions}</div>
			</div>
			${errorsHtml}
			<div class="record-layout">
				<section class="panel">
					<div class="record-summary">
						<div>
							<div class="label">Status</div>
							${badge(d.status)}
						</div>
						<div class="field">
							<div class="label">Owner / Creator</div>
							<div class="value">${esc(d.owner || 'System')}</div>
						</div>
						<div class="field">
							<div class="label">Created Date</div>
							<div class="value">${dateText(d.creation)}</div>
						</div>
						<div class="field">
							<div class="label">Last Modified</div>
							<div class="value">${dateText(d.modified)}</div>
						</div>
					</div>

					<div class="tabs" role="tablist">
						${[
							['details', 'Details'],
							['attachments', `Attachments (${d.attachments.length})`],
							['history', `Activity (${d.history.length})`],
							['related', 'Linked Records']
						].map(([t, l]) => `
							<button role="tab" aria-selected="${currentTab === t}" data-doc-tab="${t}" class="${currentTab === t ? 'active' : ''}" ${isEditing && t !== 'details' ? 'disabled' : ''}>${l}</button>
						`).join('')}
					</div>

					<div class="tab-body" style="padding:20px;">
						${renderTabContent()}
					</div>
				</section>

				<div class="side-stack">
					<section class="side-panel">
						<div class="next-label">NEXT ACTION</div>
						<h3>${getNextActionTitle(d)}</h3>
						<p>${getNextActionText(d)}</p>
						<div class="label" style="margin-top:20px">DocType</div>
						<div class="value">${esc(d.doctype)}</div>
					</section>

					<section class="side-panel">
						<h3>Readiness & Validation</h3>
						<div class="check ${d.docstatus === 1 ? '' : 'pending'}">
							<span class="mark">${d.docstatus === 1 ? '✓' : '○'}</span>
							Native ERPNext Submission
						</div>
						<div class="check ${d.attachments.length > 0 ? '' : 'pending'}">
							<span class="mark">${d.attachments.length > 0 ? '✓' : '○'}</span>
							Attachments (${d.attachments.length} attached)
						</div>
						<div class="check ${d.permissions.write ? '' : 'pending'}">
							<span class="mark">${d.permissions.write ? '✓' : '○'}</span>
							Write Permission
						</div>
					</section>
				</div>
			</div>
		`;

		attachDocEvents();
	}

	function getNextActionTitle(d) {
		if (d.docstatus === 1) return 'Document Submitted';
		if (d.docstatus === 2) return 'Document Cancelled';
		if (d.permissions.submit) return 'Submit for Review';
		return 'Complete Document Details';
	}

	function getNextActionText(d) {
		if (d.docstatus === 1) return 'This record is submitted in ERPNext and locked against further edits.';
		if (d.docstatus === 2) return 'This record has been cancelled in ERPNext.';
		if (d.permissions.submit) return 'Review all fields and child table items, then submit the document.';
		return 'Update the document fields and save changes.';
	}

	function renderTabContent() {
		const d = currentDoc;
		if (currentTab === 'details') return renderDetailsTab();
		if (currentTab === 'attachments') return renderAttachmentsTab();
		if (currentTab === 'history') return renderHistoryTab();
		if (currentTab === 'related') return renderRelatedTab();
		return '';
	}

	function renderDetailsTab() {
		const d = currentDoc;
		if (isEditing) {
			return renderEditDetailsForm();
		}

		// Read Only Details View
		let fieldsHtml = '<div class="fields">';
		for (const fm of d.fields_meta) {
			const val = d.fields[fm.fieldname];
			let displayVal = val;
			if (fm.fieldtype === 'Date' || fm.fieldtype === 'Datetime') {
				displayVal = dateText(val);
			} else if (['Currency', 'Float'].includes(fm.fieldtype)) {
				displayVal = val !== null && val !== undefined ? money(val) : '—';
			} else if (fm.fieldtype === 'Check') {
				displayVal = val ? 'Yes' : 'No';
			} else if (fm.fieldtype === 'Link') {
				displayVal = val ? `<a href="#record/${fm.options}/${encodeURIComponent(val)}"><strong>${esc(val)}</strong> →</a>` : '<span class="muted">Not set</span>';
			} else if (val === null || val === undefined || val === '') {
				displayVal = '<span class="muted">Not entered</span>';
			} else {
				displayVal = esc(val);
			}

			fieldsHtml += `
				<div class="field ${fm.fieldtype === 'Small Text' || fm.fieldtype === 'Long Text' ? 'wide' : ''}">
					<div class="label">${esc(fm.label)}</div>
					<div class="value">${displayVal}</div>
				</div>
			`;
		}
		fieldsHtml += '</div>';

		// Child Tables Read Mode
		let tablesHtml = '';
		for (const tf of d.table_fields) {
			const rows = d.tables[tf.fieldname] || [];
			tablesHtml += `
				<div style="margin-top:28px;">
					<h3 class="section-title">${esc(tf.label)}</h3>
					<div class="table-wrap">
						<table class="line-table">
							<thead>
								<tr>
									${tf.columns.slice(0, 7).map(c => `<th>${esc(c.label)}</th>`).join('')}
								</tr>
							</thead>
							<tbody>
								${rows.map(r => `
									<tr>
										${tf.columns.slice(0, 7).map(c => {
											const v = r[c.fieldname];
											return `<td>${['Currency', 'Float'].includes(c.fieldtype) ? money(v) : esc(v || '—')}</td>`;
										}).join('')}
									</tr>
								`).join('') || '<tr><td colspan="7" class="muted">No table rows entered.</td></tr>'}
							</tbody>
						</table>
					</div>
				</div>
			`;
		}

		return fieldsHtml + tablesHtml;
	}

	function renderEditDetailsForm() {
		const d = currentDoc;
		if (!editData) {
			editData = {
				fields: { ...d.fields },
				tables: JSON.parse(JSON.stringify(d.tables))
			};
		}

		let fieldsHtml = '<form id="doc-edit-form" novalidate><div class="fields">';
		for (const fm of d.fields_meta) {
			if (fm.read_only) continue;
			const val = editData.fields[fm.fieldname] !== undefined ? editData.fields[fm.fieldname] : '';
			const name = `field:${fm.fieldname}`;

			let inputHtml = '';
			if (fm.fieldtype === 'Select' && fm.options) {
				const opts = fm.options.split('\n').filter(Boolean);
				inputHtml = `<select name="${name}">${opts.map(o => `<option value="${esc(o)}" ${o == val ? 'selected' : ''}>${esc(o)}</option>`).join('')}</select>`;
			} else if (fm.fieldtype === 'Small Text' || fm.fieldtype === 'Long Text' || fm.fieldtype === 'Text Editor') {
				inputHtml = `<textarea name="${name}">${esc(val)}</textarea>`;
			} else if (fm.fieldtype === 'Date') {
				inputHtml = `<input type="date" name="${name}" value="${esc(val)}">`;
			} else if (['Int', 'Float', 'Currency', 'Percent'].includes(fm.fieldtype)) {
				inputHtml = `<input type="number" step="any" name="${name}" value="${esc(val)}">`;
			} else if (fm.fieldtype === 'Check') {
				inputHtml = `<input type="checkbox" name="${name}" ${val ? 'checked' : ''}>`;
			} else {
				inputHtml = `<input type="text" name="${name}" value="${esc(val)}">`;
			}

			fieldsHtml += `
				<label class="field ${fm.fieldtype === 'Small Text' || fm.fieldtype === 'Long Text' ? 'wide' : ''}">
					${esc(fm.label)} ${fm.reqd ? '<span class="required">*</span>' : ''}
					${inputHtml}
				</label>
			`;
		}
		fieldsHtml += '</div>';

		// Editable Child Tables
		let tablesHtml = '';
		for (const tf of d.table_fields) {
			const rows = editData.tables[tf.fieldname] || [];
			const cols = tf.columns.slice(0, 6);

			tablesHtml += `
				<div style="margin-top:28px;">
					<div class="split">
						<h3 class="section-title">${esc(tf.label)}</h3>
						<button type="button" class="button small" data-doc-action="add-table-row" data-table="${tf.fieldname}">+ Add Row</button>
					</div>
					<div class="table-wrap">
						<table class="line-table">
							<thead>
								<tr>
									${cols.map(c => `<th>${esc(c.label)}</th>`).join('')}
									<th></th>
								</tr>
							</thead>
							<tbody>
								${rows.map((r, i) => `
									<tr>
										${cols.map(c => `
											<td>
												<input name="table:${tf.fieldname}:${i}:${c.fieldname}" value="${esc(r[c.fieldname] || '')}" ${['Float', 'Currency', 'Int'].includes(c.fieldtype) ? 'type="number" step="any"' : 'type="text"'}>
											</td>
										`).join('')}
										<td>
											<button type="button" class="icon-button" data-doc-action="remove-table-row" data-table="${tf.fieldname}" data-index="${i}">×</button>
										</td>
									</tr>
								`).join('')}
							</tbody>
						</table>
					</div>
				</div>
			`;
		}

		fieldsHtml += tablesHtml + `
			<div class="form-actions" style="margin-top:24px;">
				<button type="button" class="button" data-doc-action="cancel-edit">Cancel</button>
				<button type="button" class="button primary" data-doc-action="save">Save Document</button>
			</div>
		</form>`;

		return fieldsHtml;
	}

	function renderAttachmentsTab() {
		const d = currentDoc;
		return `
			<div class="split">
				<h3>Attached Files</h3>
				<label class="button primary" style="cursor:pointer">
					+ Upload File
					<input type="file" id="doc-file-upload-input" style="display:none">
				</label>
			</div>
			<p class="muted" style="margin-bottom:15px">Upload files connected to ${esc(d.doctype)} · ${esc(d.name)} in MariaDB.</p>
			<div class="table-wrap">
				<table>
					<thead>
						<tr>
							<th>File Name</th>
							<th>Size</th>
							<th>Uploaded Date</th>
							<th>Action</th>
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
						`).join('') || '<tr><td colspan="4" class="muted">No attachments linked to this document yet.</td></tr>'}
					</tbody>
				</table>
			</div>
		`;
	}

	function renderHistoryTab() {
		const d = currentDoc;
		return `
			<h3>Activity & Audit History</h3>
			<div class="timeline" style="margin-bottom:24px;">
				${d.history.map(h => `
					<div class="event">
						<strong>${esc(h.action)}</strong>
						<small>${esc(h.actor)} · ${dateText(h.time)}</small>
					</div>
				`).join('')}
			</div>
		`;
	}

	function renderRelatedTab() {
		const d = currentDoc;
		const links = [];

		for (const fm of d.fields_meta) {
			if (fm.fieldtype === 'Link' && d.fields[fm.fieldname]) {
				links.push({
					label: fm.label,
					doctype: fm.options,
					name: d.fields[fm.fieldname]
				});
			}
		}

		return `
			<h3>Linked ERPNext Records</h3>
			<p class="muted" style="margin-bottom:15px">Records directly connected to ${esc(d.name)}.</p>
			<div class="quick-grid">
				${links.map(l => `
					<a class="quick" href="#record/${encodeURIComponent(l.doctype)}/${encodeURIComponent(l.name)}" style="text-decoration:none">
						<span class="plus">↗</span>
						${esc(l.label)}: ${esc(l.name)}
						<small>${esc(l.doctype)}</small>
					</a>
				`).join('') || '<p class="muted">No direct linked documents found in fields.</p>'}
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
			} else if (key.startsWith('table:')) {
				const [, tableField, idxStr, colField] = key.split(':');
				const idx = Number(idxStr);
				if (editData.tables[tableField] && editData.tables[tableField][idx]) {
					editData.tables[tableField][idx][colField] = val;
				}
			}
		}
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

		// Action Handlers
		view.querySelectorAll('[data-doc-action]').forEach(btn => {
			btn.onclick = async (e) => {
				e.preventDefault();
				const action = btn.dataset.docAction;

				if (action === 'edit') {
					isEditing = true;
					editData = {
						fields: { ...currentDoc.fields },
						tables: JSON.parse(JSON.stringify(currentDoc.tables))
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
						if (typeof notify === 'function') notify('Saved changes to ERPNext database.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						docErrors = [err.message];
						renderDocumentView();
					}
				} else if (action === 'submit') {
					if (!confirm(`Are you sure you want to submit ${currentDoc.name}? This will lock the document in ERPNext.`)) return;
					try {
						btn.disabled = true;
						const updated = await window.frappeDocApi.submitDetail(currentDoc.doctype, currentDoc.name);
						currentDoc = updated;
						if (typeof notify === 'function') notify('Document submitted successfully.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						alert(err.message);
					}
				} else if (action === 'cancel') {
					if (!confirm(`Are you sure you want to cancel ${currentDoc.name}?`)) return;
					try {
						btn.disabled = true;
						const updated = await window.frappeDocApi.cancelDetail(currentDoc.doctype, currentDoc.name);
						currentDoc = updated;
						if (typeof notify === 'function') notify('Document cancelled.');
						renderDocumentView();
					} catch (err) {
						btn.disabled = false;
						alert(err.message);
					}
				} else if (action === 'delete') {
					if (!confirm(`Are you sure you want to permanently delete ${currentDoc.name}?`)) return;
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
				} else if (action === 'add-table-row') {
					collectFormData();
					const tableField = btn.dataset.table;
					if (!editData.tables[tableField]) editData.tables[tableField] = [];
					editData.tables[tableField].push({});
					renderDocumentView();
				} else if (action === 'remove-table-row') {
					collectFormData();
					const tableField = btn.dataset.table;
					const idx = Number(btn.dataset.index);
					if (editData.tables[tableField]) {
						editData.tables[tableField].splice(idx, 1);
					}
					renderDocumentView();
				}
			};
		});

		// File Upload Handler
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
						if (typeof notify === 'function') notify('File attached to document.');
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
