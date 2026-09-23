import glob
for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('eco-banner', 'premium-banner')
    c = c.replace('eco-tag', 'premium-tag')
    c = c.replace('Eco Verified', 'Premium Property')
    c = c.replace('Eco', 'Premium')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(c)

