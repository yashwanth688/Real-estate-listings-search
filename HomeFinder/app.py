import os
import re
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Property, Favorite, Inquiry
from forms import LoginForm, RegisterForm, ProfileForm, PropertyForm, InquiryForm
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import func, distinct

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=['200 per day', '50 per hour'])


@app.template_filter('currency')
def currency_filter(value):
    try:
        v = float(value)
        if v >= 10000000:
            return f'\u20b9{v/10000000:.2f} Cr'
        elif v >= 100000:
            return f'\u20b9{v/100000:.2f} L'
        else:
            return f'\u20b9{v:,.0f}'
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
    total_listings = Property.query.count()
    total_agents = User.query.filter(User.role.in_(['agent', 'admin'])).count()
    locations = db.session.query(Property.location).distinct().all()
    cities = set()
    for (loc,) in locations:
        if ',' in loc:
            cities.add(loc.split(',')[-1].strip())
        else:
            cities.add(loc.strip())
    total_cities = len(cities)
    stats = {
        'total_listings': total_listings,
        'total_agents': total_agents,
        'total_cities': total_cities,
    }
    return render_template('index.html', properties=featured, stats=stats)


@app.route('/listings')
def listings():
    page = request.args.get('page', 1, type=int)
    keyword   = request.args.get('keyword', '').strip()
    location  = request.args.get('location', '').strip()
    prop_type = request.args.get('type', '').strip()
    status    = request.args.get('status', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    bedrooms  = request.args.get('bedrooms', '').strip()
    sort      = request.args.get('sort', 'newest')
    amenity   = request.args.get('amenity', '').strip()

    query = Property.query

    if keyword:
        kw = f'%{keyword}%'
        query = query.filter(
            db.or_(Property.title.ilike(kw), Property.description.ilike(kw), Property.location.ilike(kw))
        )
    if location:
        query = query.filter(Property.location.ilike(f'%{location}%'))
    if prop_type:
        query = query.filter(Property.property_type == prop_type)
    if status:
        query = query.filter(Property.status == status)

    min_price_val = None
    max_price_val = None
    if min_price:
        try:
            min_price_val = float(min_price)
            query = query.filter(Property.price >= min_price_val)
        except ValueError:
            pass
    if max_price:
        try:
            max_price_val = float(max_price)
        except ValueError:
            pass

    if bedrooms:
        try:
            query = query.filter(Property.bedrooms >= int(bedrooms))
        except ValueError:
            pass

    if amenity:
        query = query.filter(Property.amenities.ilike(f'%{amenity}%'))

    if sort == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort == 'area_asc':
        query = query.order_by(Property.area.asc())
    elif sort == 'area_desc':
        query = query.order_by(Property.area.desc())
    else:
        query = query.order_by(Property.created_at.desc())

    has_budget_filter = max_price_val is not None
    if has_budget_filter:
        exact_query = query.filter(Property.price <= max_price_val)
    else:
        exact_query = query

    paginated = exact_query.paginate(page=page, per_page=12, error_out=False)
    properties = paginated.items
    suggestions = []
    budget_miss = False

    if has_budget_filter and len(properties) == 0:
        budget_miss = True
        suggestions = query.limit(6).all()

    user_favs = set()
    if 'user_id' in session:
        favs = Favorite.query.filter_by(user_id=session['user_id']).all()
        user_favs = {f.property_id for f in favs}

    active_filters = request.args.to_dict()
    active_filters.pop('page', None)

    return render_template('listings.html',
        properties=properties,
        pagination=paginated,
        suggestions=suggestions,
        budget_miss=budget_miss,
        user_favs=user_favs,
        total_count=paginated.total if not budget_miss else 0,
        filters=active_filters
    )


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

    city = prop.location.split(',')[-1].strip() if ',' in prop.location else prop.location
    similar = Property.query.filter(
        Property.location.ilike(f'%{city}%'),
        Property.property_type == prop.property_type,
        Property.id != id
    ).limit(3).all()

    if len(similar) < 3:
        more = Property.query.filter(
            Property.property_type == prop.property_type,
            Property.id != id,
            ~Property.id.in_([s.id for s in similar])
        ).limit(3 - len(similar)).all()
        similar.extend(more)

    form = InquiryForm()
    return render_template('property_details.html',
        property=prop, agent=agent,
        is_favorite=is_favorite, similar=similar, form=form)


@app.route('/property/<int:id>/inquire', methods=['POST'])
@limiter.limit('5 per minute')
def inquire(id):
    form = InquiryForm()
    if form.validate_on_submit():
        inquiry = Inquiry(
            property_id=id,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data
        )
        db.session.add(inquiry)
        db.session.commit()
        flash('Your inquiry has been sent! The agent will contact you soon.', 'success')
    else:
        flash('Please fill all required fields correctly.', 'error')
    return redirect(url_for('property_details', id=id))


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('10 per hour')
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please log in.', 'error')
        else:
            user = User(
                name=form.name.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                role=form.role.data
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
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
            flash(f"Welcome back, {user.name}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
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
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)


@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash('Please log in to view your saved properties.', 'info')
        return redirect(url_for('login'))
    favs = Favorite.query.filter_by(user_id=session['user_id']).order_by(Favorite.created_at.desc()).all()
    props = [f.property for f in favs if f.property]
    user_favs = {p.id for p in props}
    return render_template('listings.html',
        properties=props,
        title='My Saved Properties',
        user_favs=user_favs,
        total_count=len(props),
        filters={},
        pagination=None,
        budget_miss=False,
        suggestions=[]
    )


@app.route('/property/<int:id>/favorite', methods=['POST'])
def toggle_favorite(id):
    if 'user_id' not in session:
        flash('Please log in to save properties.', 'info')
        return redirect(url_for('login'))
    fav = Favorite.query.filter_by(user_id=session['user_id'], property_id=id).first()
    if fav:
        db.session.delete(fav)
        flash('Removed from your saved properties.', 'info')
    else:
        db.session.add(Favorite(user_id=session['user_id'], property_id=id))
        flash('Property saved to your favourites!', 'success')
    db.session.commit()
    next_url = request.form.get('next') or request.referrer or url_for('property_details', id=id)
    return redirect(next_url)


@app.route('/manage')
def manage_listings():
    if 'user_id' not in session or session.get('role') not in ['agent', 'admin']:
        flash('Access restricted to agents and admins.', 'error')
        return redirect(url_for('index'))

    if session.get('role') == 'admin':
        props = Property.query.order_by(Property.created_at.desc()).all()
        stats = {
            'total_listings': len(props),
            'sale_listings': sum(1 for p in props if p.status == 'Sale'),
            'rent_listings': sum(1 for p in props if p.status == 'Rent'),
            'total_users': User.query.count(),
            'total_inquiries': Inquiry.query.count(),
            'is_admin': True
        }
    else:
        props = Property.query.filter_by(agent_id=session['user_id']).order_by(Property.created_at.desc()).all()
        stats = {
            'total_listings': len(props),
            'sale_listings': sum(1 for p in props if p.status == 'Sale'),
            'rent_listings': sum(1 for p in props if p.status == 'Rent'),
            'total_favorites': sum(len(p.favorites) for p in props),
            'total_inquiries': sum(len(p.inquiries) for p in props),
            'is_admin': False
        }
    return render_template('manage_listings.html', properties=props, stats=stats)


@app.route('/manage/inquiries')
def manage_inquiries():
    if 'user_id' not in session or session.get('role') not in ['agent', 'admin']:
        return redirect(url_for('index'))
    if session.get('role') == 'admin':
        inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    else:
        my_prop_ids = [p.id for p in Property.query.filter_by(agent_id=session['user_id']).all()]
        inquiries = Inquiry.query.filter(Inquiry.property_id.in_(my_prop_ids)).order_by(Inquiry.created_at.desc()).all()
    return render_template('inquiries.html', inquiries=inquiries)


@app.route('/property/add', methods=['GET', 'POST'])
def add_property():
    if 'user_id' not in session or session.get('role') not in ['agent', 'admin']:
        flash('You must be an agent to add properties.', 'error')
        return redirect(url_for('index'))
    form = PropertyForm()
    if form.validate_on_submit():
        img_url = 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&q=80'
        if form.image.data and form.image.data.filename:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = url_for('static', filename='uploads/' + filename)
        prop = Property(
            agent_id=session['user_id'],
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            location=form.location.data,
            property_type=form.property_type.data,
            status=form.status.data,
            bedrooms=form.bedrooms.data or 0,
            bathrooms=form.bathrooms.data or 0,
            area=form.area.data,
            image_url=img_url,
            amenities=form.amenities.data or ''
        )
        db.session.add(prop)
        db.session.commit()
        flash('Property listed successfully!', 'success')
        return redirect(url_for('manage_listings'))
    return render_template('add_property.html', form=form)


@app.route('/property/<int:id>/edit', methods=['GET', 'POST'])
def edit_property(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    prop = db.session.get(Property, id)
    if not prop:
        abort(404)
    if prop.agent_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorised to edit this property.', 'error')
        return redirect(url_for('manage_listings'))
    form = PropertyForm(obj=prop)
    if form.validate_on_submit():
        if form.image.data and form.image.data.filename:
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
        prop.amenities = form.amenities.data or ''
        db.session.commit()
        flash('Property updated successfully!', 'success')
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
        flash('Property deleted successfully.', 'success')
    else:
        flash('You are not authorised to delete this property.', 'error')
    return redirect(url_for('manage_listings'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('404.html'), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template('404.html'), 403


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
