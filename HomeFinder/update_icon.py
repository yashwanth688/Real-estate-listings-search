with open('templates/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('<i data-lucide="leaf"></i>', '<i data-lucide="star"></i>')
c = c.replace('🌱', '⭐')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('templates/listings.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('<i data-lucide="leaf"></i>', '<i data-lucide="star"></i>')

with open('templates/listings.html', 'w', encoding='utf-8') as f:
    f.write(c)
