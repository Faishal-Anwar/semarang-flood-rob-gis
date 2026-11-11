with open("generate_thematic_maps.py", "r") as f:
    text = f.read()
text = text.replace(", letter_spacing=2", "")
with open("generate_thematic_maps.py", "w") as f:
    f.write(text)
print("Fixed letter_spacing in generate_thematic_maps.py")
