app_name = "its_ui_redesign"
app_title = "ITS Project Operations"
app_publisher = "Betaedge"
app_description = "Custom Vue 3 Enterprise Portal for Construction and Project Operations"
app_email = "info@betaedge.com"
app_license = "MIT"

website_route_rules = [
    {"from_route": "/portal-access", "to_route": "portal_access"},
    {"from_route": "/portal", "to_route": "portal"},
    {"from_route": "/portal/<path:app_path>", "to_route": "portal"},
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
