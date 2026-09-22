/**
 * ITS ERP Review - Universal Export Engine
 * Provides CSV (with UTF-8 BOM) and Microsoft Excel SpreadsheetML (.xls)
 * download functionality for all list views, operational grids, and registers.
 */
(function(window) {
	'use strict';

	function formatTimestamp() {
		const d = new Date();
		const pad = n => String(n).padStart(2, '0');
		return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
	}

	function sanitizeFilename(name) {
		return (name || 'Export')
			.replace(/[^a-zA-Z0-9_\-\u0600-\u06FF]/g, '_')
			.replace(/_+/g, '_')
			.slice(0, 80);
	}

	function xmlEscape(str) {
		if (str === null || str === undefined) return '';
		return String(str)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&apos;');
	}

	function cleanCellText(text) {
		if (!text) return '';
		return String(text)
			.replace(/[\r\n\t]+/g, ' ')
			.replace(/\s+/g, ' ')
			.trim();
	}

	function triggerDownload(blob, filename) {
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.style.display = 'none';
		a.href = url;
		a.download = filename;
		document.body.appendChild(a);
		a.click();
		setTimeout(() => {
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
		}, 250);
	}

	/**
	 * Export data to RFC 4180 CSV with UTF-8 BOM
	 */
	function downloadCSV(filename, headers, rows) {
		const safeName = (filename.endsWith('.csv') ? filename : `${filename}.csv`);
		const escapeCsvField = (val) => {
			if (val === null || val === undefined) return '';
			let s = String(val);
			if (s.includes('"') || s.includes(',') || s.includes('\n') || s.includes('\r')) {
				s = `"${s.replace(/"/g, '""')}"`;
			}
			return s;
		};

		const lines = [];
		if (headers && headers.length) {
			lines.push(headers.map(escapeCsvField).join(','));
		}
		for (const row of rows) {
			lines.push(row.map(escapeCsvField).join(','));
		}

		// \uFEFF ensures UTF-8 BOM so Excel opens non-ASCII characters / Arabic correctly
		const csvContent = '\uFEFF' + lines.join('\r\n');
		const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
		triggerDownload(blob, safeName);

		if (window.notify) {
			window.notify(`Exported ${rows.length} rows to ${safeName}`);
		}
	}

	/**
	 * Export data to Microsoft Excel XML SpreadsheetML (.xls)
	 * Fully styled with corporate ITS Navy header and tabular cell types.
	 */
	function downloadExcel(filename, sheetName, headers, rows) {
		const safeName = (filename.endsWith('.xls') ? filename : `${filename}.xls`);
		const safeSheet = (sheetName || 'Data').slice(0, 31).replace(/[:\\\/\?\*\[\]]/g, ' ');

		let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
		xml += '<?mso-application progid="Excel.Sheet"?>\n';
		xml += '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\n';
		xml += '  xmlns:o="urn:schemas-microsoft-com:office:office"\n';
		xml += '  xmlns:x="urn:schemas-microsoft-com:office:excel"\n';
		xml += '  xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"\n';
		xml += '  xmlns:html="http://www.w3.org/TR/REC-html40">\n';
		xml += '  <DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">\n';
		xml += '    <Author>Independent Technical Services (ITS)</Author>\n';
		xml += `    <Created>${new Date().toISOString()}</Created>\n`;
		xml += '    <Company>Independent Technical Services LLC</Company>\n';
		xml += '  </DocumentProperties>\n';
		xml += '  <Styles>\n';
		xml += '    <Style ss:ID="Default" ss:Name="Normal">\n';
		xml += '      <Alignment ss:Vertical="Center"/>\n';
		xml += '      <Font ss:FontName="Segoe UI" ss:Size="10" ss:Color="#192A43"/>\n';
		xml += '    </Style>\n';
		xml += '    <Style ss:ID="HeaderStyle">\n';
		xml += '      <Alignment ss:Horizontal="Center" ss:Vertical="Center" ss:WrapText="1"/>\n';
		xml += '      <Borders>\n';
		xml += '        <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#071F4E"/>\n';
		xml += '        <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#071F4E"/>\n';
		xml += '        <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#071F4E"/>\n';
		xml += '        <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#071F4E"/>\n';
		xml += '      </Borders>\n';
		xml += '      <Font ss:FontName="Segoe UI" ss:Size="10" ss:Bold="1" ss:Color="#FFFFFF"/>\n';
		xml += '      <Interior ss:Color="#071F4E" ss:Pattern="Solid"/>\n';
		xml += '    </Style>\n';
		xml += '    <Style ss:ID="DataCell">\n';
		xml += '      <Alignment ss:Vertical="Center"/>\n';
		xml += '      <Borders>\n';
		xml += '        <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E6EE"/>\n';
		xml += '        <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E6EE"/>\n';
		xml += '        <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E6EE"/>\n';
		xml += '      </Borders>\n';
		xml += '      <Font ss:FontName="Segoe UI" ss:Size="9.5" ss:Color="#192A43"/>\n';
		xml += '    </Style>\n';
		xml += '    <Style ss:ID="NumberCell">\n';
		xml += '      <Alignment ss:Horizontal="Right" ss:Vertical="Center"/>\n';
		xml += '      <Borders>\n';
		xml += '        <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E6EE"/>\n';
		xml += '        <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E6EE"/>\n';
		xml += '        <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E6EE"/>\n';
		xml += '      </Borders>\n';
		xml += '      <Font ss:FontName="Segoe UI" ss:Size="9.5" ss:Color="#192A43"/>\n';
		xml += '      <NumberFormat ss:Format="#,##0.00"/>\n';
		xml += '    </Style>\n';
		xml += '  </Styles>\n';
		xml += `  <Worksheet ss:Name="${xmlEscape(safeSheet)}">\n`;
		xml += '    <Table>\n';

		// Headers
		if (headers && headers.length) {
			xml += '      <Row ss:Height="26">\n';
			for (const h of headers) {
				xml += `        <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">${xmlEscape(cleanCellText(h))}</Data></Cell>\n`;
			}
			xml += '      </Row>\n';
		}

		// Data rows
		for (const row of rows) {
			xml += '      <Row ss:Height="20">\n';
			for (const cell of row) {
				const cleaned = cleanCellText(cell);
				// Test if purely numeric
				const isNum = typeof cell === 'number' || (/^-?\d+(\.\d+)?$/.test(cleaned) && !cleaned.startsWith('0') && cleaned !== '');
				if (isNum) {
					const numVal = Number(cleaned);
					xml += `        <Cell ss:StyleID="NumberCell"><Data ss:Type="Number">${numVal}</Data></Cell>\n`;
				} else {
					xml += `        <Cell ss:StyleID="DataCell"><Data ss:Type="String">${xmlEscape(cleaned)}</Data></Cell>\n`;
				}
			}
			xml += '      </Row>\n';
		}

		xml += '    </Table>\n';
		xml += '    <WorksheetOptions xmlns="urn:schemas-microsoft-com:office:excel">\n';
		xml += '      <Selected/>\n';
		xml += '      <FreezePanes/>\n';
		xml += '      <FrozenNoSplit/>\n';
		xml += '      <SplitHorizontal>1</SplitHorizontal>\n';
		xml += '      <TopRowBottomPane>1</TopRowBottomPane>\n';
		xml += '      <ActivePane>2</ActivePane>\n';
		xml += '      <Panes><Pane><Number>3</Number></Pane><Pane><Number>2</Number><ActiveRow>1</ActiveRow></Pane></Panes>\n';
		xml += '      <ProtectObjects>False</ProtectObjects>\n';
		xml += '      <ProtectScenarios>False</ProtectScenarios>\n';
		xml += '    </WorksheetOptions>\n';
		xml += '  </Worksheet>\n';
		xml += '</Workbook>';

		const blob = new Blob([xml], { type: 'application/vnd.ms-excel;charset=utf-8;' });
		triggerDownload(blob, safeName);

		if (window.notify) {
			window.notify(`Exported ${rows.length} rows to ${safeName}`);
		}
	}

	/**
	 * Extract data from an HTML table element and export it
	 */
	function exportTableElement(tableEl, baseName, format) {
		if (!tableEl) return;

		const thead = tableEl.querySelector('thead');
		const tbody = tableEl.querySelector('tbody') || tableEl;

		const headers = [];
		const skipColIndices = new Set();

		if (thead) {
			const ths = thead.querySelectorAll('tr:last-child th');
			ths.forEach((th, idx) => {
				const text = cleanCellText(th.innerText || th.textContent);
				if (!text || text.toLowerCase() === 'actions' || text.toLowerCase() === 'action') {
					skipColIndices.add(idx);
				} else {
					headers.push(text);
				}
			});
		}

		const rows = [];
		const trs = tbody.querySelectorAll('tr');
		trs.forEach(tr => {
			const tds = tr.querySelectorAll('td');
			if (!tds.length) return;
			// Skip "no records" empty state placeholder rows
			if (tds.length === 1 && (tds[0].getAttribute('colspan') > 2 || tds[0].textContent.includes('No records') || tds[0].textContent.includes('No entries') || tds[0].textContent.includes('No materials') || tds[0].textContent.includes('No files'))) {
				return;
			}

			const rowData = [];
			tds.forEach((td, idx) => {
				if (skipColIndices.has(idx)) return;
				// Clone to extract text without button contents
				const clone = td.cloneNode(true);
				// Remove buttons and icons that shouldn't pollute export
				clone.querySelectorAll('button, .chevron, .task-icon, [data-action="remove-line"]').forEach(el => el.remove());
				const cellText = cleanCellText(clone.innerText || clone.textContent);
				rowData.push(cellText);
			});
			if (rowData.length) {
				rows.push(rowData);
			}
		});

		const timestamp = formatTimestamp();
		const safeTitle = sanitizeFilename(baseName || document.title || 'ITS_List');
		const filename = `${safeTitle}_${timestamp}`;

		if (format === 'excel') {
			downloadExcel(filename, safeTitle, headers, rows);
		} else {
			downloadCSV(filename, headers, rows);
		}
	}

	/**
	 * Build export buttons HTML snippet for tables and toolbars
	 */
	function renderExportButtons(options = {}) {
		const targetId = options.targetId ? `data-target-table="${options.targetId}"` : '';
		const title = options.title ? `data-export-title="${options.title}"` : '';
		const customSource = options.source ? `data-export-source="${options.source}"` : '';

		return `
			<div class="list-export-tools" ${targetId} ${title} ${customSource}>
				<span class="export-label">Export:</span>
				<button type="button" class="button small export-btn export-btn-csv" data-action="export-csv" title="Download whole list as CSV">⬇ CSV</button>
				<button type="button" class="button small export-btn export-btn-excel" data-action="export-excel" title="Download whole list as Excel spreadsheet">⬇ Excel</button>
			</div>
		`;
	}

	// Global event delegation for export buttons
	document.addEventListener('click', function(e) {
		const btn = e.target.closest('[data-action="export-csv"], [data-action="export-excel"]');
		if (!btn) return;
		e.preventDefault();
		e.stopPropagation();

		const format = btn.dataset.action === 'export-excel' ? 'excel' : 'csv';
		const tools = btn.closest('.list-export-tools') || btn.closest('.toolbar') || btn.closest('.panel-head') || btn.parentElement;

		let baseTitle = tools?.dataset?.exportTitle;
		if (!baseTitle) {
			const headingEl = document.querySelector('#view h1') || document.querySelector('#view h2');
			baseTitle = headingEl ? headingEl.textContent.trim() : (window.location.hash.slice(1) || 'ITS_Records');
		}

		// Check if a specific target table is specified
		let tableEl = null;
		if (tools && tools.dataset && tools.dataset.targetTable) {
			tableEl = document.getElementById(tools.dataset.targetTable);
		}
		if (!tableEl) {
			// Find closest table or within current panel / section
			const panel = btn.closest('.panel') || btn.closest('.table-wrap') || document.getElementById('view');
			tableEl = panel ? panel.querySelector('table') : document.querySelector('table');
		}

		if (tableEl) {
			exportTableElement(tableEl, baseTitle, format);
		} else {
			if (window.notify) {
				window.notify('No list data available to export.');
			}
		}
	});

	window.itsExport = {
		downloadCSV,
		downloadExcel,
		exportTableElement,
		renderExportButtons,
		sanitizeFilename
	};

})(window);
