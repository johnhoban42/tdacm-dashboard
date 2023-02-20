from setuptools import setup

requirements = open("requirements.txt").readlines()

setup(
    name="tdacm-dashboard",
    author="John Hoban",
    author_email="johnhoban4@gmail.com",
    description="Realtime dashboard for the Rutgers TDACM Capstone",
    url="https://github.com/johnhoban42/tdacm-dashboard",
    requires=requirements,
)
