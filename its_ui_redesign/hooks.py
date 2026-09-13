app_name = "its_ui_redesign"
app_title = "ITS Project Operations"
app_publisher = "Betaedge"
app_description = "Custom Vue 3 Enterprise Portal for Construction and Project Operations"
app_email = "info@betaedge.com"
app_license = "MIT"

favicon = "/assets/its_ui_redesign/images/its_logo.png"

website_context = {
    "favicon": "/assets/its_ui_redesign/images/its_logo.png",
    "splash_image": "/assets/its_ui_redesign/images/its_logo.png"
}

website_route_rules = [
    {"from_route": "/portal-access", "to_route": "portal_access"},
    {"from_route": "/portal", "to_route": "portal"},
    {"from_route": "/portal/<path:app_path>", "to_route": "portal"},
    {"from_route": "/its-print", "to_route": "its_print"},
]

fixtures = [
    {"dt": "Role", "filters": [["name", "in", [
        "Portal Administrator",
        "Project Manager",
        "Project Engineer",
        "Planning Engineer",
        "Estimation Engineer",
        "Procurement Manager",
        "Store Manager",
        "HR Manager",
        "Finance Manager",
        "Accountant",
        "Fabrication Manager",
        "Equipment Manager",
        "Management Viewer"
    ]]]}
]

doc_events = {
    "Purchase Order": {
        "validate": "its_ui_redesign.api.common.validate_purchase_order_hard_stop",
        "on_submit": "its_ui_redesign.api.common.validate_purchase_order_hard_stop"
    },
    "Delivery Note": {
        "on_submit": "its_ui_redesign.api.common.validate_delivery_note_hard_stop"
    },
    "Sales Invoice": {
        "on_submit": "its_ui_redesign.api.common.validate_sales_invoice_hard_stop"
    }
}

jinja = {
    "methods": [
        "its_ui_redesign.utils.print_helpers.its_print_company",
        "its_ui_redesign.utils.print_helpers.its_print_sections",
        "its_ui_redesign.utils.print_helpers.its_print_tables",
        "its_ui_redesign.utils.print_helpers.get_its_doctype_title",
        "its_ui_redesign.utils.print_helpers.get_its_doc_items",
        "its_ui_redesign.utils.print_helpers.get_its_doc_totals",
        "its_ui_redesign.utils.print_helpers.get_its_field_groups",
        "its_ui_redesign.utils.print_helpers.get_its_child_tables",
        "its_ui_redesign.utils.print_helpers.get_its_logo_data_uri"
    ]
}



