from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="its_ui_redesign",
    version="0.0.1",
    description="ITS Project Operations - Custom Vue 3 Enterprise Portal for ERPNext",
    author="Betaedge",
    author_email="info@betaedge.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
