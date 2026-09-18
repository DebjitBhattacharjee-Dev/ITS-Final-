app_name = "its_erp_review"
app_title = "ITS ERP Review Portal"
app_publisher = "ITS"
app_description = "Production-grade Custom ERP Review Portal running alongside ERPNext/Frappe"
app_email = "admin@its.com"
app_license = "MIT"
app_version = "1.0.0"

website_route_rules = [
    {"from_route": "/review-print", "to_route": "review_print"},
    {"from_route": "/review", "to_route": "review"},
    {"from_route": "/review/<path:app_path>", "to_route": "review"}
]

jenv = {
    "methods": [
        "its_erp_review.utils.print_helpers.its_print_company",
        "its_erp_review.utils.print_helpers.its_print_sections",
        "its_erp_review.utils.print_helpers.its_print_tables",
        "its_erp_review.utils.print_helpers.get_its_logo_data_uri",
        "its_erp_review.utils.print_helpers.get_its_doctype_title",
        "its_erp_review.utils.print_helpers.get_its_doc_items",
        "its_erp_review.utils.print_helpers.get_its_doc_totals",
        "its_erp_review.utils.print_helpers.get_its_field_groups",
        "its_erp_review.utils.print_helpers.get_its_child_tables",
    ]
}

home_page = "review"
required_apps = ["frappe"]
