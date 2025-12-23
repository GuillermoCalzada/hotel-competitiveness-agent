from setuptools import setup, find_packages

setup(
    name="hotel-competitiveness-agent",
    version="1.0.0",
    description="Agente de IA para análisis de competitividad hotelera",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tu Nombre",
    author_email="tu.email@ejemplo.com",
    url="https://github.com/tuusuario/hotel-competitiveness-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Business",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.29.0",
        "pandas>=2.1.4",
        "numpy>=1.24.3",
        "plotly>=5.17.0",
        "scikit-learn>=1.3.2",
        "seaborn>=0.13.0",
        "matplotlib>=3.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hotel-agent=streamlit_app.main:main",
        ],
    },
)
