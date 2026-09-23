import re

# Update property_details.html
with open('templates/property_details.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Map HTML
map_html = '''<div class="property-map box-panel mt-4">
    <h3>Location Map</h3>
    <div id="map" style="height: 300px; width: 100%; border-radius: 8px; z-index: 1;" data-location="{{ property.location }}"></div>
</div>
'''
content = content.replace('<div class="property-description box-panel">', map_html + '<div class="property-description box-panel mt-4">')

# Add Form fields
form_fields = '''{{ form.hidden_tag() }}
                    <div class="form-group">
                        {{ form.name(placeholder="Your Name *") }}
                    </div>
                    <div class="form-group">
                        {{ form.email(placeholder="Your Email *") }}
                    </div>
                    <div class="form-group">
                        {{ form.phone(placeholder="Your Phone") }}
                    </div>
                    <div class="form-group">
                        {{ form.message(placeholder="I am interested in this property...", rows="4") }}
                    </div>
                    {{ form.submit(class="btn btn-primary btn-block") }}'''
content = re.sub(r'<div class="form-group">.*?<button.*?/button>', form_fields, content, flags=re.DOTALL)

# Add Map Script block
script_block = '''{% block scripts %}
<script>
    document.addEventListener("DOMContentLoaded", function() {
        var mapEl = document.getElementById('map');
        if (mapEl) {
            var location = mapEl.getAttribute('data-location');
            // Fallback default coordinates
            var map = L.map('map').setView([40.7128, -74.0060], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            
            // Geocode using Nominatim API
            fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(location))
                .then(res => res.json())
                .then(data => {
                    if (data && data.length > 0) {
                        var lat = data[0].lat;
                        var lon = data[0].lon;
                        map.setView([lat, lon], 14);
                        L.marker([lat, lon]).addTo(map).bindPopup(location).openPopup();
                    }
                });
        }
    });
</script>
{% endblock %}'''
content = content.rsplit('{% endblock %}', 1)
content = script_block + '\n{% endblock %}'.join(content)

content = content.replace('<form action="{{ url_for(\'toggle_favorite\', id=property.id) }}" method="POST">', '<form action="{{ url_for(\'toggle_favorite\', id=property.id) }}" method="POST">\n                            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">')

with open('templates/property_details.html', 'w', encoding='utf-8') as f:
    f.write(content)

def update_auth_template(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('<form action="{{ url_for(\'login\') }}" method="POST" class="auth-form">', '<form action="{{ url_for(\'login\') }}" method="POST" class="auth-form">\n                {{ form.hidden_tag() }}')
    c = c.replace('<form action="{{ url_for(\'register\') }}" method="POST" class="auth-form">', '<form action="{{ url_for(\'register\') }}" method="POST" class="auth-form">\n                {{ form.hidden_tag() }}')
    c = re.sub(r'<input type="email" name="email".*?>', '{{ form.email(placeholder="Email Address") }}', c)
    c = re.sub(r'<input type="password" name="password".*?>', '{{ form.password(placeholder="Password") }}', c)
    c = re.sub(r'<input type="text" name="name".*?>', '{{ form.name(placeholder="Full Name") }}', c)
    c = re.sub(r'<select name="role".*?</select>', '{{ form.role() }}', c, flags=re.DOTALL)
    c = re.sub(r'<button type="submit".*?>.*?</button>', '{{ form.submit(class="btn btn-primary btn-block") }}', c)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(c)

update_auth_template('templates/login.html')
update_auth_template('templates/register.html')

with open('templates/listings.html', 'r', encoding='utf-8') as f:
    c = f.read()
pagination_html = '''
        {% if pagination %}
        <div class="pagination mt-4 text-center">
            {% if pagination.has_prev %}
                <a href="{{ url_for('listings', page=pagination.prev_num, keyword=request.args.get('keyword'), location=request.args.get('location'), type=request.args.get('type'), status=request.args.get('status')) }}" class="btn btn-outline">&laquo; Prev</a>
            {% endif %}
            <span class="page-info" style="margin: 0 1rem; line-height: 2.5rem;">Page {{ pagination.page }} of {{ pagination.pages }}</span>
            {% if pagination.has_next %}
                <a href="{{ url_for('listings', page=pagination.next_num, keyword=request.args.get('keyword'), location=request.args.get('location'), type=request.args.get('type'), status=request.args.get('status')) }}" class="btn btn-outline">Next &raquo;</a>
            {% endif %}
        </div>
        {% endif %}
'''
if '{% endblock %}' in c:
    c = c.replace('{% endblock %}', pagination_html + '\n{% endblock %}')
with open('templates/listings.html', 'w', encoding='utf-8') as f:
    f.write(c)

def update_property_form(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('class="property-form">', 'class="property-form" enctype="multipart/form-data">\n                {{ form.hidden_tag() }}')
    c = re.sub(r'<input type="text" name="title".*?>', '{{ form.title() }}', c)
    c = re.sub(r'<input type="number".*?name="price".*?>', '{{ form.price() }}', c)
    c = re.sub(r'<input type="text" name="location".*?>', '{{ form.location() }}', c)
    c = re.sub(r'<input type="number" name="bedrooms".*?>', '{{ form.bedrooms() }}', c)
    c = re.sub(r'<input type="number" name="bathrooms".*?>', '{{ form.bathrooms() }}', c)
    c = re.sub(r'<input type="number" name="area".*?>', '{{ form.area() }}', c)
    c = re.sub(r'<input type="text" name="image_url".*?>', '{{ form.image() }}', c)
    c = re.sub(r'<input type="url" name="image_url".*?>', '{{ form.image() }}', c)
    c = re.sub(r'<textarea name="description".*?>.*?</textarea>', '{{ form.description(rows="5") }}', c, flags=re.DOTALL)
    c = re.sub(r'<textarea name="amenities".*?>.*?</textarea>', '{{ form.amenities(rows="3") }}', c, flags=re.DOTALL)
    c = re.sub(r'<select name="property_type".*?</select>', '{{ form.property_type() }}', c, flags=re.DOTALL)
    c = re.sub(r'<select name="status".*?</select>', '{{ form.status() }}', c, flags=re.DOTALL)
    c = re.sub(r'<button type="submit".*?>.*?</button>', '{{ form.submit(class="btn btn-primary") }}', c)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(c)

update_property_form('templates/add_property.html')
try: update_property_form('templates/edit_property.html')
except: pass

with open('templates/manage_listings.html', 'r', encoding='utf-8') as f:
    c = f.read()
stats_html = '''
        {% if stats %}
        <div class="dashboard-stats" style="display: flex; gap: 1rem; margin-bottom: 2rem;">
            <div class="stat-card box-panel" style="flex: 1; text-align: center;">
                <h3 style="font-size: 2rem; color: var(--primary-color);">{{ stats.total_listings }}</h3>
                <p class="text-muted">Total Listings</p>
            </div>
            {% if session.role == 'admin' %}
            <div class="stat-card box-panel" style="flex: 1; text-align: center;">
                <h3 style="font-size: 2rem; color: var(--primary-color);">{{ stats.total_users }}</h3>
                <p class="text-muted">Total Users</p>
            </div>
            {% else %}
            <div class="stat-card box-panel" style="flex: 1; text-align: center;">
                <h3 style="font-size: 2rem; color: var(--primary-color);">{{ stats.total_favorites }}</h3>
                <p class="text-muted">Saved by Users</p>
            </div>
            {% endif %}
            <div class="stat-card box-panel" style="flex: 1; text-align: center;">
                <h3 style="font-size: 2rem; color: var(--primary-color);">{{ stats.total_inquiries }}</h3>
                <p class="text-muted">Inquiries</p>
            </div>
        </div>
        {% endif %}
'''
c = c.replace('<div class="section-header">', stats_html + '\n        <div class="section-header">')
c = c.replace('<form action="{{ url_for(\'delete_property\', id=property.id) }}" method="POST" style="display: inline;">', '<form action="{{ url_for(\'delete_property\', id=property.id) }}" method="POST" style="display: inline;">\n                                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">')
with open('templates/manage_listings.html', 'w', encoding='utf-8') as f:
    f.write(c)
