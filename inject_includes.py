import os
import re

html_dir = "c:/Users/Vardhaman Industries/OneDrive/Documents/Projects/Fruit Analysis Using Machine Learning/Fruit Analysis Using Machine Learning/templates"

exclude = ["footer.html", "background.html"]

for filename in os.listdir(html_dir):
    if filename.endswith(".html") and filename not in exclude:
        filepath = os.path.join(html_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Add background.html right after <body ...>
        # Check if already included so it's idempotent
        if "{% include 'background.html' %}" not in content and '{% include "background.html" %}' not in content:
            content = re.sub(r'(<body[^>]*>)', r'\1\n    {% include "background.html" %}', content, count=1)
            
        # 2. Replace existing <footer>...</footer> with include
        if "<footer" in content:
            content = re.sub(r'<footer.*?</footer>', '{% include "footer.html" %}', content, flags=re.DOTALL)
        else:
            # If no footer, insert right before </body> or script tags
            if "{% include 'footer.html' %}" not in content and '{% include "footer.html" %}' not in content:
                content = content.replace("</body>", "    {% include 'footer.html' %}\n  </body>")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Done processing templates.")
