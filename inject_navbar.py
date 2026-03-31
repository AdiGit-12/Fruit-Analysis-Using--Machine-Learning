import os
import re

html_dir = "c:/Users/Vardhaman Industries/OneDrive/Documents/Projects/Fruit Analysis Using Machine Learning/Fruit Analysis Using Machine Learning/templates"
files = ["index.html", "about.html", "prediction.html", "contact.html"]

for filename in files:
    filepath = os.path.join(html_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace the block starting with <!-- Header --> and ending after <!-- Mobile menu --> ... </div>
    # The regex approach: Look for <!-- Header --> to the specific closing robustly, or just rely on the fact that it's between <!-- Header --> and the section right after (which is <!-- Main Content --> or <!-- Hero Section --> or similar).
    
    # Actually, a simple regex from <!-- Header --> up to the end of <div id="mobile-menu">...</div>
    # We can match `<!-- Header -->` and then `<!-- .*? -->` to find the start of the next section.
    
    pattern = re.compile(r'<!-- Header -->.*?<!-- Mobile menu -->.*?</div>\n\s*</div>\n', re.DOTALL)
    
    # Wait, the mobile menu ends with:
    #     {% endif %}
    #   </div>
    # </div>
    # So we can match up to </div>\n    </div>
    
    # Let's use a safer regex:
    # Replace from <!-- Header --> to <!-- (Hero Section|Main Content) -->
    
    parts = re.split(r'(<!-- (Hero Section|Main Content|Section) -->)', content, maxsplit=1)
    if len(parts) > 1:
        # Before the section comment, find <!-- Header -->
        header_split = parts[0].split("<!-- Header -->")
        if len(header_split) > 1:
            page_name = filename.replace(".html", "")
            
            new_nav = f'{{% set active_page = "{page_name}" %}}\n    {{% include "navbar.html" %}}\n\n    '
            content = header_split[0] + new_nav + parts[1] + "".join(parts[2:])
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                print(f"Updated {filename}")

print("Done processing specific templates.")
