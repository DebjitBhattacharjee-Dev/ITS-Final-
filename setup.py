from setuptools import setup, find_packages

setup(
	name="its_erp_review",
	version="1.0.0",
	description="Production-grade Custom ERP Review Portal running alongside ERPNext/Frappe",
	author="ITS",
	author_email="admin@its.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=[]
)
