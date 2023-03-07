from setuptools import setup

requirements = open("requirements.txt").readlines()

setup(
    name="tdacm-dashboard",
    version="1.0.0",
    author="John Hoban",
    author_email="johnhoban4@gmail.com",
    description="Realtime dashboard for the Rutgers TDACM Capstone",
    url="https://github.com/johnhoban42/tdacm-dashboard",
    install_requires=requirements,
    entry_points={"console_scripts": ["tdacm = tdacm.cli:cli"]},
    package_data={"tdacm": ["assets/*.css"]},
    include_package_data=True,
)
