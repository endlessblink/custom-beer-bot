from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="whatsapp-summarizer-bot",
    version="1.0.0",
    author="Author",
    author_email="author@example.com",
    description="A bot that summarizes WhatsApp group messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/whatsapp-summarizer-bot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "whatsapp-bot=src.main:main",
        ],
    },
) 