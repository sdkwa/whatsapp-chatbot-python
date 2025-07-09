#!/usr/bin/env python3
"""Setup script for SDKWA WhatsApp Chatbot."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sdkwa-whatsapp-chatbot",
    version="1.0.0",
    author="SDKWA Community",
    author_email="support@sdkwa.pro",
    description="WhatsApp Chatbot library for Python based on SDKWA API with Telegraf-like interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sdkwa/whatsapp-chatbot-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=[
        "sdkwa-whatsapp-api-client>=1.0.3",
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "webhook": [
            "flask>=2.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
        ],
    },
    keywords=[
        "whatsapp",
        "chatbot",
        "sdkwa",
        "telegraf",
        "messaging",
        "api",
        "bot",
        "automation",
    ],
    project_urls={
        "Documentation": "https://docs.sdkwa.pro",
        "Source": "https://github.com/sdkwa/whatsapp-chatbot-python",
        "Tracker": "https://github.com/sdkwa/whatsapp-chatbot-python/issues",
    },
)
