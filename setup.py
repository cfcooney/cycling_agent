from setuptools import setup, find_packages

setup(
    name="cycling_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "langchain-openai>=0.0.5",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.8",
)
