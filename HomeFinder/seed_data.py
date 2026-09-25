import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Property, Favorite, Inquiry

CITIES_LOCALITIES = {
    'Mumbai': ['Andheri', 'Powai', 'Bandra', 'Thane', 'Navi Mumbai', 'Worli', 'Juhu'],
    'Delhi': ['Dwarka', 'Vasant Kunj', 'Rohini', 'Hauz Khas', 'Saket', 'Connaught Place'],
    'Bengaluru': ['Whitefield', 'Electronic City', 'Koramangala', 'HSR Layout', 'Marathahalli', 'Hebbal'],
    'Hyderabad': ['Gachibowli', 'Madhapur', 'Kondapur', 'Kukatpally', 'Miyapur', 'Banjara Hills'],
    'Chennai': ['Anna Nagar', 'OMR', 'Velachery', 'Adyar', 'Tambaram', 'T Nagar'],
    'Pune': ['Hinjewadi', 'Baner', 'Wakad', 'Kharadi', 'Viman Nagar', 'Magarpatta'],
    'Kolkata': ['Salt Lake', 'Rajarhat', 'New Town', 'Ballygunge', 'Alipore'],
    'Ahmedabad': ['SG Highway', 'Bopal', 'Vastrapur', 'Satellite', 'Thaltej'],
    'Visakhapatnam': ['Madhurawada', 'MVP Colony', 'Gajuwaka', 'Siripuram', 'Seethammadhara'],
    'Chandigarh': ['Sector 17', 'Zirakpur', 'Mohali', 'Panchkula'],
    'Jaipur': ['Malviya Nagar', 'Vaishali Nagar', 'Mansarovar', 'Jagatpura'],
    'Lucknow': ['Gomti Nagar', 'Aliganj', 'Hazratganj', 'Indira Nagar']
}

AMENITIES_LIST = ['Parking', 'Swimming Pool', 'Gym', 'Security', 'Balcony', 'Garden', 'Lift', 'Power Backup', 'Furnished', 'Air Conditioning', 'CCTV', 'Gated Community']

PROPERTY_TYPES = ['Apartment', 'House', 'Villa', 'Plot', 'Commercial']

def generate_properties(agent_id, num=250):
    properties = []
    for _ in range(num):
        city = random.choice(list(CITIES_LOCALITIES.keys()))
        locality = random.choice(CITIES_LOCALITIES[city])
        prop_type = random.choice(PROPERTY_TYPES)
        status = random.choices(['Sale', 'Rent'], weights=[0.7, 0.3])[0]
        
        # Budget Logic
        if status == 'Sale':
            if prop_type in ['Villa', 'Commercial']: price = random.randint(150, 800) * 100000
            elif prop_type == 'Apartment': price = random.randint(30, 300) * 100000
            else: price = random.randint(15, 100) * 100000
        else:
            price = random.randint(10, 150) * 1000
        
        bedrooms = random.randint(1, 5) if prop_type not in ['Plot', 'Commercial'] else 0
        bathrooms = bedrooms + random.randint(0, 1) if bedrooms > 0 else 0
        
        if prop_type == 'Plot': area = random.randint(1000, 5000)
        elif prop_type == 'Commercial': area = random.randint(500, 10000)
        else: area = random.randint(500, 4000)
        
        num_amenities = random.randint(2, 7)
        amenities = ', '.join(random.sample(AMENITIES_LIST, num_amenities))
        
        images = [
            'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80',
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',
            'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',
            'https://images.unsplash.com/photo-1449844908441-8829872d2607?w=800&q=80',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80',
            'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80'
        ]
        
        title_prefix = 'Luxurious' if price > 10000000 else 'Modern'
        title = f"{title_prefix} {bedrooms} BHK {prop_type} in {locality}"
        if prop_type in ['Plot', 'Commercial']: title = f"Prime {prop_type} Space in {locality}"
        
        p = Property(
            agent_id=agent_id,
            title=title,
            description=f"A beautiful {prop_type.lower()} located in the prime area of {locality}, {city}. Features modern amenities and great connectivity.",
            price=price,
            location=f"{locality}, {city}",
            property_type=prop_type,
            status=status,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            area=area,
            image_url=random.choice(images),
            amenities=amenities,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        properties.append(p)
    return properties

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Clean existing data safely
        Inquiry.query.delete()
        Favorite.query.delete()
        Property.query.delete()
        
        admin = User.query.filter_by(email='admin@homefinder.com').first()
        if not admin:
            admin = User(name='Admin User', email='admin@homefinder.com', password_hash=generate_password_hash('password123'), role='admin')
            db.session.add(admin)
        
        agent = User.query.filter_by(email='john@example.com').first()
        if not agent:
            agent = User(name='John Doe (Agent)', email='john@example.com', password_hash=generate_password_hash('password123'), role='agent')
            db.session.add(agent)
            
        db.session.commit()
        
        print('Generating 250 properties...')
        props = generate_properties(agent.id, 250)
        db.session.bulk_save_objects(props)
        db.session.commit()
        print('Database successfully seeded with Indian properties!')
