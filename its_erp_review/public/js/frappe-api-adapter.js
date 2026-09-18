/* Frappe API Adapter for ITS ERP Review Portal */
(function(window) {
	const originalFetch = window.fetch;

	window.frappeFetchAdapter = async function(url, options = {}) {
		options.headers = options.headers || {};
		options.headers['X-Frappe-CSRF-Token'] = window.csrf_token || frappe?.csrf_token || '';

		// Intercept prototype API endpoints and map to native Frappe whitelisted methods
		if (url.startsWith('/api/records')) {
			if (!options.method || options.method === 'GET') {
				const res = await originalFetch('/api/method/its_erp_review.api.documents.get_records', {
					method: 'GET',
					headers: options.headers
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			} else if (options.method === 'PUT' || options.method === 'POST') {
				const payload = JSON.parse(options.body || '{}');
				const res = await originalFetch('/api/method/its_erp_review.api.documents.save_records', {
					method: 'POST',
					headers: { ...options.headers, 'Content-Type': 'application/json' },
					body: JSON.stringify({ revision: payload.revision, records: payload.records })
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			}
		}

		if (url.startsWith('/api/workspace')) {
			if (!options.method || options.method === 'GET') {
				const res = await originalFetch('/api/method/its_erp_review.api.documents.get_workspace', {
					method: 'GET',
					headers: options.headers
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			} else if (options.method === 'PUT' || options.method === 'POST') {
				const payload = JSON.parse(options.body || '{}');
				const res = await originalFetch('/api/method/its_erp_review.api.documents.save_workspace', {
					method: 'POST',
					headers: { ...options.headers, 'Content-Type': 'application/json' },
					body: JSON.stringify({ state: payload.state, revision: payload.revision })
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			}
		}

		if (url.startsWith('/api/parties')) {
			if (!options.method || options.method === 'GET') {
				const res = await originalFetch('/api/method/its_erp_review.api.directories.get_parties', {
					method: 'GET',
					headers: options.headers
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			} else if (options.method === 'POST') {
				const payload = JSON.parse(options.body || '{}');
				const res = await originalFetch('/api/method/its_erp_review.api.directories.save_party', {
					method: 'POST',
					headers: { ...options.headers, 'Content-Type': 'application/json' },
					body: JSON.stringify({ party: payload })
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			}
		}

		if (url.startsWith('/api/materials')) {
			if (!options.method || options.method === 'GET') {
				const res = await originalFetch('/api/method/its_erp_review.api.materials.get_materials', {
					method: 'GET',
					headers: options.headers
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			} else if (options.method === 'POST') {
				const payload = JSON.parse(options.body || '{}');
				const res = await originalFetch('/api/method/its_erp_review.api.materials.save_material', {
					method: 'POST',
					headers: { ...options.headers, 'Content-Type': 'application/json' },
					body: JSON.stringify({ material: payload })
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			}
		}

		if (url.startsWith('/api/registers')) {
			const urlObj = new URL(url, window.location.origin);
			const parts = urlObj.pathname.split('/').filter(Boolean);
			const kind = parts[2];

			if (kind === 'files' && parts[3]) {
				window.location.href = `/api/method/its_erp_review.api.attachments.download_file?file_id=${encodeURIComponent(parts[3])}`;
				return new Response(JSON.stringify({ ok: true }), { status: 200 });
			}

			if (!options.method || options.method === 'GET') {
				const res = await originalFetch(`/api/method/its_erp_review.api.registers.get_registers?kind=${kind || ''}`, {
					method: 'GET',
					headers: options.headers
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			} else if (options.method === 'POST') {
				const payload = JSON.parse(options.body || '{}');
				const res = await originalFetch('/api/method/its_erp_review.api.registers.save_register', {
					method: 'POST',
					headers: { ...options.headers, 'Content-Type': 'application/json' },
					body: JSON.stringify({ kind: kind, record: payload })
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			}
		}

		if (url.startsWith('/api/attachments')) {
			const urlObj = new URL(url, window.location.origin);
			const parts = urlObj.pathname.split('/').filter(Boolean);
			if (parts.length > 2 && parts[2]) {
				window.location.href = `/api/method/its_erp_review.api.attachments.download_file?file_id=${encodeURIComponent(parts[2])}`;
				return new Response(JSON.stringify({ ok: true }), { status: 200 });
			}

			if (!options.method || options.method === 'GET') {
				const res = await originalFetch('/api/method/its_erp_review.api.attachments.get_attachments', {
					method: 'GET',
					headers: options.headers
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			} else if (options.method === 'POST') {
				const payload = JSON.parse(options.body || '{}');
				const res = await originalFetch('/api/method/its_erp_review.api.attachments.upload_attachment', {
					method: 'POST',
					headers: { ...options.headers, 'Content-Type': 'application/json' },
					body: JSON.stringify(payload)
				});
				const json = await res.json();
				return new Response(JSON.stringify(json.message || json), { status: res.status });
			}
		}

		return originalFetch(url, options);
	};

	// Override window.fetch for API route calls
	window.fetch = window.frappeFetchAdapter;

	// Single-Record ERPNext Document API helper methods
	window.frappeDocApi = {
		async getDetail(doctype, name) {
			const res = await originalFetch(`/api/method/its_erp_review.api.documents.get_document_detail?doctype=${encodeURIComponent(doctype || '')}&name=${encodeURIComponent(name || '')}`, {
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' }
			});
			const json = await res.json();
			if (!res.ok) {
				const err = new Error(json._server_messages ? JSON.parse(json._server_messages)[0] : (json.exception || json.message || 'Error loading document'));
				err.status = res.status;
				err.exc_type = json.exc_type;
				throw err;
			}
			return json.message || json;
		},
		async saveDetail(doctype, name, data) {
			const res = await originalFetch('/api/method/its_erp_review.api.documents.save_document_detail', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || ''
				},
				body: JSON.stringify({ doctype, name, data })
			});
			const json = await res.json();
			if (!res.ok) {
				let msg = json.message || 'Error saving document';
				if (json._server_messages) {
					try {
						const parsed = JSON.parse(json._server_messages);
						msg = parsed.map(m => JSON.parse(m).message).join('; ');
					} catch (e) {}
				}
				const err = new Error(msg);
				err.status = res.status;
				throw err;
			}
			return json.message || json;
		},
		async submitDetail(doctype, name) {
			const res = await originalFetch('/api/method/its_erp_review.api.documents.submit_document_detail', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || ''
				},
				body: JSON.stringify({ doctype, name })
			});
			const json = await res.json();
			if (!res.ok) {
				let msg = json.message || 'Error submitting document';
				if (json._server_messages) {
					try {
						const parsed = JSON.parse(json._server_messages);
						msg = parsed.map(m => JSON.parse(m).message).join('; ');
					} catch (e) {}
				}
				throw new Error(msg);
			}
			return json.message || json;
		},
		async cancelDetail(doctype, name) {
			const res = await originalFetch('/api/method/its_erp_review.api.documents.cancel_document_detail', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || ''
				},
				body: JSON.stringify({ doctype, name })
			});
			const json = await res.json();
			if (!res.ok) {
				let msg = json.message || 'Error cancelling document';
				if (json._server_messages) {
					try {
						const parsed = JSON.parse(json._server_messages);
						msg = parsed.map(m => JSON.parse(m).message).join('; ');
					} catch (e) {}
				}
				throw new Error(msg);
			}
			return json.message || json;
		},
		async deleteDetail(doctype, name) {
			const res = await originalFetch('/api/method/its_erp_review.api.documents.delete_document_detail', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || ''
				},
				body: JSON.stringify({ doctype, name })
			});
			const json = await res.json();
			if (!res.ok) {
				throw new Error(json.message || 'Error deleting document');
			}
			return json.message || json;
		},
		async getDetail(doctype, name) {
			const persona = window.currentPersona || '';
			const res = await originalFetch(`/api/method/its_erp_review.api.documents.get_document_detail?doctype=${encodeURIComponent(doctype || '')}&name=${encodeURIComponent(name || '')}&active_persona=${encodeURIComponent(persona)}`, {
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' }
			});
			const json = await res.json();
			if (!res.ok) {
				const err = new Error(json.message || 'Document could not be retrieved');
				err.status = res.status;
				err.exc_type = json.exc_type;
				throw err;
			}
			return json.message || json;
		},
		async transitionWorkflow(doctype, name, action, comments = '', persona = null) {
			const activePersona = persona || window.currentPersona || '';
			const res = await originalFetch('/api/method/its_erp_review.api.documents.transition_document_workflow', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || ''
				},
				body: JSON.stringify({ doctype, name, action, comments, persona: activePersona })
			});
			const json = await res.json();
			if (!res.ok) {
				let msg = json.message || 'Workflow transition failed';
				if (json._server_messages) {
					try {
						const parsed = JSON.parse(json._server_messages);
						msg = parsed.map(m => JSON.parse(m).message).join('; ');
					} catch (e) {}
				}
				throw new Error(msg);
			}
			return json.message || json;
		},
		async setActivePersona(persona) {
			const res = await originalFetch('/api/method/its_erp_review.api.permissions.set_active_persona', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || ''
				},
				body: JSON.stringify({ persona })
			});
			const json = await res.json();
			if (res.ok && json.message) {
				window.currentPersona = json.message.active_persona;
			}
			return json.message || json;
		},
		async getPrint(doctype, name) {
			const res = await originalFetch(`/api/method/its_erp_review.api.documents.get_document_print?doctype=${encodeURIComponent(doctype || '')}&name=${encodeURIComponent(name || '')}`, {
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' }
			});
			const json = await res.json();
			if (!res.ok) {
				throw new Error(json.message || 'Error fetching print document');
			}
			return json.message || json;
		}
	};
})(window);

