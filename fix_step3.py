with open("step3_generate_documentation.py", "r") as f:
    text = f.read()

text = text.replace("import matplotlib.patches as mpatches\nimport numpy as np", "import matplotlib.patches as mpatches\nimport matplotlib.lines as mlines\nimport numpy as np")
with open("step3_generate_documentation.py", "w") as f:
    f.write(text)
print("Fixed mlines import in step3_generate_documentation.py")
