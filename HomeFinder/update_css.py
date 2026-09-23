with open('static/css/style.css', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('linear-gradient(135deg, #0f2010 0%, #14532d 60%, #15803d 100%)', 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #1d4ed8 100%)')
c = c.replace('linear-gradient(135deg, #14532d 0%, #16a34a 100%)', 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)')
c = c.replace('Eco-Friendly Professional Theme', 'Professional Corporate Theme')
c = c.replace('ECO BANNER', 'PREMIUM BANNER')
c = c.replace('.eco-tag', '.premium-tag')
c = c.replace('eco-banner', 'premium-banner')

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(c)

