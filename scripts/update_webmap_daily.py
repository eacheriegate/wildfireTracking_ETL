import os

# Run each step of the ETL and visualization workflow
os.system("python scripts/extract.py")
os.system("python scripts/transform.py")
os.system("python scripts/visualize.py")

