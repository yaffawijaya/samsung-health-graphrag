from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Retrieve environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"""
OPENAI_API_KEY: {OPENAI_API_KEY}
NEO4J_URI: {NEO4J_URI}
NEO4J_USERNAME: {NEO4J_USERNAME}
NEO4J_PASSWORD: {NEO4J_PASSWORD}
""")
