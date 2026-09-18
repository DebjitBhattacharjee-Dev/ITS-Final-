app_name = "its_erp_review"
app_title = "ITS ERP Review Portal"
app_publisher = "ITS"
app_description = "Production-grade Custom ERP Review Portal running alongside ERPNext/Frappe"
app_email = "admin@its.com"
app_license = "MIT"
app_version = "1.0.0"

# Routing rules: Map /review and /review/* to www/review/index.html
website_route_rules = [
    {"from_route": "/review/<path:app_path>", "to_route": "review"},
    {"from_route": "/review", "to_route": "review"}
]

# Standard home page route if requested
home_page = "review"

# Required app dependencies
required_apps = ["frappe"]
