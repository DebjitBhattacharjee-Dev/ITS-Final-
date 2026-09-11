import api from "./frappe"

export async function getDocumentList(doctype, options = {}) {
  const { page = 1, pageLength = 20, filters = {}, searchText = "", fields = null, orderBy = null } = options
  const response = await api.get("/api/method/its_ui_redesign.api.common.get_document_list", {
    params: {
      doctype,
      filters: JSON.stringify(filters),
      fields: fields ? JSON.stringify(fields) : null,
      order_by: orderBy,
      page,
      page_length: pageLength,
      search_text: searchText
    }
  })
  return response.data.message || response.data
}

export async function getDocumentDetail(doctype, name) {
  const response = await api.get("/api/method/its_ui_redesign.api.common.get_document_detail", {
    params: { doctype, name }
  })
  return response.data.message || response.data
}

export async function getNewDocumentTemplate(doctype) {
  const response = await api.get("/api/method/its_ui_redesign.api.common.get_new_document_template", {
    params: { doctype }
  })
  return response.data.message || response.data
}

export async function saveDocument(doctype, docData) {
  const response = await api.post("/api/method/its_ui_redesign.api.common.save_document", {
    doctype,
    doc_data: JSON.stringify(docData)
  })
  return response.data.message || response.data
}

export async function submitDocument(doctype, name) {
  const response = await api.post("/api/method/its_ui_redesign.api.common.submit_document", {
    doctype,
    name
  })
  return response.data.message || response.data
}

export async function cancelDocument(doctype, name) {
  const response = await api.post("/api/method/its_ui_redesign.api.common.cancel_document", {
    doctype,
    name
  })
  return response.data.message || response.data
}

export async function amendDocument(doctype, name) {
  const response = await api.post("/api/method/its_ui_redesign.api.common.amend_document", {
    doctype,
    name
  })
  return response.data.message || response.data
}

export async function applyWorkflowAction(doctype, name, action) {
  const response = await api.post("/api/method/its_ui_redesign.api.common.apply_workflow_action", {
    doctype,
    name,
    action
  })
  return response.data.message || response.data
}

export async function searchLinkOptions(doctype, txt = "", filters = {}) {
  const response = await api.get("/api/method/its_ui_redesign.api.common.search_link_options", {
    params: { doctype, txt, filters: JSON.stringify(filters) }
  })
  return response.data.message || response.data
}

export async function getDocTypeMeta(doctype) {
  const response = await api.get("/api/method/its_ui_redesign.api.common.get_doctype_meta", {
    params: { doctype }
  })
  return response.data.message || response.data
}

export async function fetchDashboardSummary() {
  const response = await api.get("/api/method/its_ui_redesign.api.dashboard.get_dashboard_summary")
  return response.data.message || response.data
}

export async function fetchDocList(doctype, fields = ["name", "modified"], filters = {}, limit = 20) {
  const res = await getDocumentList(doctype, { fields, filters, pageLength: limit })
  return res.data || []
}


export async function fetchWorkspaceDashboard(workspaceId, filters = {}) {
  return callApi('its_ui_redesign.api.common.get_workspace_dashboard', {
    workspace_id: workspaceId,
    ...filters
  })
}


export async function getRelatedDocuments(doctype, name) {
  return callApi("its_ui_redesign.api.common.get_related_documents", { doctype, name })
}

export async function validateSupplierPORelease(purchaseOrderName) {
  return callApi("its_ui_redesign.api.common.validate_supplier_po_release", { purchase_order_name: purchaseOrderName })
}

export async function getDocumentPdf(doctype, name, printFormat = null, letterhead = null) {
  return callApi("its_ui_redesign.api.common.get_document_pdf", { doctype, name, print_format: printFormat, letterhead })
}


export async function getContextualCreateOptions(doctype) {
  return callApi("its_ui_redesign.api.common.get_contextual_create_options", { doctype })
}

export async function getCreateTargetPayload(sourceDocType, sourceName, targetDocType) {
  return callApi("its_ui_redesign.api.common.get_create_target_payload", {
    source_doctype: sourceDocType,
    source_name: sourceName,
    target_doctype: targetDocType
  })
}

export async function validateClientPOMatch(quotationName, customerPOAmount) {
  return callApi("its_ui_redesign.api.common.validate_client_po_match", {
    quotation_name: quotationName,
    customer_po_amount: customerPOAmount
  })
}
