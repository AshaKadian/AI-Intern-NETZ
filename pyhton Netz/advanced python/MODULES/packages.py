# Create a Directory: Make a directory for your package. This will serve as the root folder.
# Add Modules: Add Python files (modules) to the directory, each representing specific functionality.
# Include __init__.py: Add an __init__.py file (can be empty) to the directory to mark it as a package.
# Add Sub packages (Optional): Create subdirectories with their own __init__.py files for sub packages.
# Import Modules: Use dot notation to import, e.g., from mypackage.module1 import greet.
# Initialize the main package
from MODULES import calculate, add, sub

# Using the placeholder calculate function
calculate()

# Perform basic operations
print("Addition:", add(5, 3))          
print("Subtraction:", sub(10, 4))



