import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Property, Favorite, Inquiry
from forms import LoginForm, RegisterForm, ProfileForm, PropertyForm, InquiryForm
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=['200 per day', '50 per hour'])

@app.template_filter('currency')
def currency_filter(value):
    try:
        return f'\u20b9{float(value):,.0f}'
    except (ValueError, TypeError):
        return value

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
    return dict(current_user=user)

@app.route('/')
def index():
    featured = Property.query.order_by(Property.created_at.desc()).limit(9).all()
    return render_template('index.html', properties=featured)

@app.route('/listings')
def listings():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()
    prop_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    sort = request.args.get('sort', 'newest')

    query = Property.query

    if keyword:
        query = query.filter(db.or_(Property.title.ilike(f'%{keyword}%'), Property.description.ilike(f'%{keyword}%'), Property.location.ilike(f'%{keyword}%')))
    if location:
        query = query.filter(Property.location.ilike(f'%{location}%'))
    if prop_type:
        query = query.filter(Property.property_type == prop_type)
    if status:
        query = query.filter(Property.status == status)
    if min_price:
        try: query = query.filter(Property.price >= float(min_price))
        except ValueError: pass
    if max_price:
        try: query = query.filter(Property.price <= float(max_price))
        except ValueError: pass

    if sort == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Property.price.desc())
    else:
        query = query.order_by(Property.created_at.desc())

    paginated = query.paginate(page=page, per_page=12, error_out=False)
    return render_template('listings.html', properties=paginated.items, pagination=paginated)

@app.route('/property/<int:id>')
def property_details(id):
    prop = db.session.get(Property, id)
    if not prop:
        abort(404)

    agent = prop.agent
    is_favorite = False
    if 'user_id' in session:
        fav = Favorite.query.filter_by(user_id=session['user_id'], property_id=id).first()
        is_favorite = bool(fav)

    similar = Property.query.filter(Property.property_type == prop.property_type, Property.id != id).limit(3).all()
    form = InquiryForm()
    return render_template('property_details.html', property=prop, agent=agent, is_favorite=is_favorite, similar=similar, form=form)

@app.route('/property/<int:id>/inquire', methods=['POST'])
@limiter.limit('5 per minute')
def inquire(id):
    form = InquiryForm()
    if form.validate_on_submit():
        inquiry = Inquiry(property_id=id, name=form.name.data, email=form.email.data, phone=form.phone.data, message=form.message.data)
        db.session.add(inquiry)
        db.session.commit()
        flash('Your inquiry has been sent!', 'success')
    else:
        flash('Please correct the errors in the form.', 'error')
    return redirect(url_for('property_details', id=id))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('10 per hour')
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
        else:
            user = User(name=form.name.data, email=form.email.data, password_hash=generate_password_hash(form.password.data), role=form.role.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.phone = form.phone.data
        db.session.commit()
        session['name'] = user.name
        flash('Profile updated.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)

@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    props = [f.property for f in favs]
    return render_template('listings.html', properties=props, title='My Saved Properties')

@app.route('/property/<int:id>/favorite', methods=['POST'])
def toggle_favorite(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    fav = Favorite.query.filter_by(user_id=session['user_id'], property_id=id).first()
    if fav:
        db.session.delete(fav)
        flash('Removed from favorites.', 'info')
    else:
        db.session.add(Favorite(user_id=session['user_id'], property_id=id))
        flash('Added to favorites!', 'success')
    db.session.commit()
    return redirect(url_for('property_details', id=id))

@app.route('/manage')
def manage_listings():
    if 'user_id' not in session or session.get('role') not in ['agent', 'admin']:
        return redirect(url_for('index'))
    
    if session.get('role') == 'admin':
        props = Property.query.all()
        stats = {
            'total_listings': len(props),
            'total_users': User.query.count(),
            'total_inquiries': Inquiry.query.count()
        }
    else:
        props = Property.query.filter_by(agent_id=session['user_id']).all()
        stats = {
            'total_listings': len(props),
            'total_favorites': sum(len(p.favorites) for p in props),
            'total_inquiries': sum(len(p.inquiries) for p in props)
        }
    return render_template('manage_listings.html', properties=props, stats=stats)

@app.route('/property/add', methods=['GET', 'POST'])
def add_property():
    if 'user_id' not in session or session.get('role') not in ['agent', 'admin']:
        return redirect(url_for('index'))
    form = PropertyForm()
    if form.validate_on_submit():
        img_url = ''
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = url_for('static', filename='uploads/' + filename)
        
        prop = Property(agent_id=session['user_id'], title=form.title.data, description=form.description.data, price=form.price.data, location=form.location.data, property_type=form.property_type.data, status=form.status.data, bedrooms=form.bedrooms.data or 0, bathrooms=form.bathrooms.data or 0, area=form.area.data, image_url=img_url, amenities=form.amenities.data)
        db.session.add(prop)
        db.session.commit()
        flash('Property added!', 'success')
        return redirect(url_for('manage_listings'))
    return render_template('add_property.html', form=form)

@app.route('/property/<int:id>/edit', methods=['GET', 'POST'])
def edit_property(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    prop = db.session.get(Property, id)
    if not prop or (prop.agent_id != session['user_id'] and session.get('role') != 'admin'):
        abort(403)
    form = PropertyForm(obj=prop)
    if form.validate_on_submit():
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            prop.image_url = url_for('static', filename='uploads/' + filename)
        prop.title = form.title.data
        prop.description = form.description.data
        prop.price = form.price.data
        prop.location = form.location.data
        prop.property_type = form.property_type.data
        prop.status = form.status.data
        prop.bedrooms = form.bedrooms.data or 0
        prop.bathrooms = form.bathrooms.data or 0
        prop.area = form.area.data
        prop.amenities = form.amenities.data
        db.session.commit()
        flash('Property updated!', 'success')
        return redirect(url_for('manage_listings'))
    return render_template('edit_property.html', form=form, property=prop)

@app.route('/property/<int:id>/delete', methods=['POST'])
def delete_property(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    prop = db.session.get(Property, id)
    if prop and (prop.agent_id == session['user_id'] or session.get('role') == 'admin'):
        db.session.delete(prop)
        db.session.commit()
        flash('Property deleted.', 'success')
    return redirect(url_for('manage_listings'))

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e): return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

