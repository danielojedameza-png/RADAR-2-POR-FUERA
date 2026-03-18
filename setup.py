from setuptools import setup, find_packages

setup(
    name="radar-agrodasin",
    version="1.0.0",
    description="Radar de oportunidades de contratación pública para el sector agropecuario colombiano",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "radar-agrodasin=radar_agrodasin.__main__:main",
        ]
    },
)
