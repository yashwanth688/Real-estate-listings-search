import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = 'homefinder.db'

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        location TEXT NOT NULL,
        property_type TEXT NOT NULL,
        status TEXT NOT NULL,
        bedrooms INTEGER DEFAULT 0,
        bathrooms INTEGER DEFAULT 0,
        area INTEGER NOT NULL,
        image_url TEXT NOT NULL,
        amenities TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        property_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
        UNIQUE(user_id, property_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
    )
    ''')

    # Insert sample users
    password = generate_password_hash('password123')
    cursor.execute("INSERT INTO users (name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
                   ('Admin User', 'admin@homefinder.com', password, '9876543210', 'admin'))
    cursor.execute("INSERT INTO users (name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
                   ('Rajesh Kumar', 'rajesh@example.com', password, '9123456780', 'agent'))

    # 50+ properties across all major Indian cities
    properties = [

        # ─── MUMBAI ──────────────────────────────────────────────────────────
        (2, '2BHK Modern Apartment in Bandra West',
         'Beautifully designed 2BHK apartment in the heart of Bandra West with stunning sea views. Fully furnished with modular kitchen and premium fittings.',
         9500000, 'Bandra West, Mumbai', 'Apartment', 'Sale', 2, 2, 1100,
         'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80',
         'Gym, Swimming Pool, Parking, Security, Lift'),

        (2, 'Spacious 3BHK Flat in Powai',
         'Well-ventilated 3BHK apartment near Powai Lake with a beautiful lake view. Close to top tech companies and Hiranandani Hospital.',
         18000, 'Powai, Mumbai', 'Apartment', 'Rent', 3, 2, 1450,
         'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80',
         'Gym, Parking, Lift, Security, Kids Play Area'),

        (2, 'Luxury 5BHK Villa in Juhu',
         'Exquisite 5BHK luxury villa near Juhu Beach with a private pool and landscaped garden. Perfect for families seeking premium living.',
         75000000, 'Juhu, Mumbai', 'Villa', 'Sale', 5, 5, 5200,
         'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',
         'Private Pool, Garden, Garage, Security System, Home Theatre'),

        (2, '1BHK Apartment in Andheri East',
         'Compact and well-maintained 1BHK apartment in Andheri East. Excellent metro connectivity and close to domestic airport.',
         5800000, 'Andheri East, Mumbai', 'Apartment', 'Sale', 1, 1, 620,
         'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=800&q=80',
         'Security, Lift, Power Backup, Parking'),

        (2, '4BHK Sea-View Flat in Worli',
         'Premium 4BHK apartment with panoramic sea views on the 22nd floor in Worli. Designed with Italian marble flooring and smart-home features.',
         55000000, 'Worli, Mumbai', 'Apartment', 'Sale', 4, 4, 2800,
         'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',
         'Concierge, Gym, Infinity Pool, Valet Parking, Helipad Access'),

        (2, '2BHK Furnished Flat in Thane',
         'Semi-furnished 2BHK flat in a gated society in Thane West near Viviana Mall. Great connectivity via Thane railway station.',
         14000, 'Thane West, Mumbai', 'Apartment', 'Rent', 2, 2, 1050,
         'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80',
         'Gym, Swimming Pool, Parking, Security, Jogging Track'),

        (2, 'Row House in Navi Mumbai',
         'Spacious 3BHK row house in a well-planned township in Kharghar, Navi Mumbai. Close to Central Park and educational institutes.',
         12500000, 'Kharghar, Navi Mumbai', 'House', 'Sale', 3, 3, 1900,
         'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80',
         'Garden, Parking, Security, Community Hall, Jogging Track'),

        # ─── DELHI / NCR ─────────────────────────────────────────────────────
        (2, '4BHK Independent House in Vasant Kunj',
         'Well-maintained 4BHK independent house in the green locality of Vasant Kunj, South Delhi. Excellent connectivity to the airport and metro.',
         32000000, 'Vasant Kunj, New Delhi', 'House', 'Sale', 4, 3, 2200,
         'https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800&q=80',
         'Terrace Garden, Parking, Servant Quarter, Solar Panels'),

        (2, '1BHK Studio Apartment in Lajpat Nagar',
         'Cozy 1BHK studio apartment for working professionals near Lajpat Nagar Market. Metro connectivity available just 500m away.',
         14000, 'Lajpat Nagar, New Delhi', 'Apartment', 'Rent', 1, 1, 600,
         'https://images.unsplash.com/photo-1560185127-6a8f94d94deb?w=800&q=80',
         'WiFi, Security, Power Backup, Lift'),

        (2, '3BHK Premium Flat in Dwarka',
         'Spacious 3BHK flat in Dwarka Sector 12 with a large balcony overlooking a park. Ideal for families with excellent social infrastructure.',
         8500000, 'Dwarka Sector 12, New Delhi', 'Apartment', 'Sale', 3, 2, 1650,
         'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80',
         'Club House, Gym, Swimming Pool, Parking, Security'),

        (2, 'Luxury Apartment in DLF Cyber City Gurugram',
         'High-rise 3BHK luxury apartment in DLF Phase 2, Gurugram. Walking distance from Cyber Hub, premium restaurants and nightlife.',
         28000, 'DLF Phase 2, Gurugram', 'Apartment', 'Rent', 3, 3, 2100,
         'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80',
         'Fully Furnished, Rooftop Pool, Gym, Concierge, Valet Parking'),

        (2, '2BHK Apartment in Noida Sector 62',
         'Modern 2BHK apartment in Noida Sector 62 IT hub. Close to Sector 62 metro station, malls and top multinational offices.',
         6200000, 'Sector 62, Noida', 'Apartment', 'Sale', 2, 2, 1150,
         'https://images.unsplash.com/photo-1416331108676-a22ccb276e35?w=800&q=80',
         'Gym, Swimming Pool, Parking, Security, Badminton Court'),

        (2, '5BHK Bungalow in Greater Noida West',
         'Spacious 5BHK independent bungalow with large front lawn in Greater Noida West. Quiet locality, great for joint families.',
         22000000, 'Greater Noida West, Noida', 'Villa', 'Sale', 5, 4, 3800,
         'https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=800&q=80',
         'Lawn, Parking, Security, Servant Quarter, Generator'),

        (2, '2BHK Flat in Indirapuram Ghaziabad',
         'Affordable and well-connected 2BHK apartment in Indirapuram, Ghaziabad. Close to NH-24, schools and shopping complexes.',
         9000, 'Indirapuram, Ghaziabad', 'Apartment', 'Rent', 2, 1, 1000,
         'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&q=80',
         'Parking, Security, Power Backup, Park'),

        # ─── BENGALURU ───────────────────────────────────────────────────────
        (2, '2BHK Apartment in Whitefield',
         'Modern 2BHK apartment in a gated community in Whitefield, close to ITPL Tech Park. Perfect for IT professionals.',
         6500000, 'Whitefield, Bengaluru', 'Apartment', 'Sale', 2, 2, 1200,
         'https://images.unsplash.com/photo-1504615755583-2916b52192a3?w=800&q=80',
         'Gym, Swimming Pool, Jogging Track, Parking, Security'),

        (2, '3BHK Furnished Flat in Koramangala',
         'Fully furnished 3BHK premium apartment in the vibrant Koramangala. Walking distance from restaurants, cafes, and shopping malls.',
         42000, 'Koramangala, Bengaluru', 'Apartment', 'Rent', 3, 3, 1800,
         'https://images.unsplash.com/photo-1560185127-6a8f94d94deb?w=800&q=80',
         'Fully Furnished, Gym, Parking, Power Backup, Security'),

        (2, '4BHK Villa in Sarjapur Road',
         'Stunning 4BHK independent villa with modern architecture in Sarjapur. Large garden and rooftop terrace included.',
         22000000, 'Sarjapur Road, Bengaluru', 'Villa', 'Sale', 4, 4, 3500,
         'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=800&q=80',
         'Garden, Rooftop Terrace, Garage, Security System, Solar Power'),

        (2, '1BHK PG-Style Flat in HSR Layout',
         'Affordable 1BHK apartment in HSR Layout, ideal for startup employees and freshers. Easy access to Electronic City via NICE Road.',
         11000, 'HSR Layout, Bengaluru', 'Apartment', 'Rent', 1, 1, 550,
         'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=800&q=80',
         'WiFi, Security, Power Backup, Water Supply'),

        (2, 'Premium 3BHK in Hebbal',
         'Premium lake-facing 3BHK apartment in Hebbal. Close to Manyata Tech Park and Kempegowda International Airport.',
         9800000, 'Hebbal, Bengaluru', 'Apartment', 'Sale', 3, 3, 1750,
         'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&q=80',
         'Lake View, Gym, Swimming Pool, Parking, Clubhouse'),

        (2, 'Independent House in JP Nagar',
         'Well-maintained 3BHK independent house in JP Nagar Phase 4. Quiet locality with easy access to metro and malls.',
         16500000, 'JP Nagar, Bengaluru', 'House', 'Sale', 3, 2, 1600,
         'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80',
         'Garden, Parking, Security, Bore Well, Solar Water Heater'),

        # ─── HYDERABAD ───────────────────────────────────────────────────────
        (2, '2BHK Apartment in HITEC City',
         'Well-maintained 2BHK apartment in HITEC City near Cyber Towers. Ideal for IT employees with all modern amenities.',
         7800000, 'HITEC City, Hyderabad', 'Apartment', 'Sale', 2, 2, 1300,
         'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80',
         'Gym, Swimming Pool, Parking, Clubhouse, Security'),

        (2, 'Luxury Penthouse in Jubilee Hills',
         'Ultra-luxury penthouse with a private terrace and 360-degree city views in Jubilee Hills. Only for the discerning buyer.',
         65000000, 'Jubilee Hills, Hyderabad', 'Apartment', 'Sale', 4, 4, 4000,
         'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',
         'Private Terrace, Concierge, Gym, Valet Parking, Smart Home System'),

        (2, '3BHK Flat in Gachibowli',
         'Semi-furnished 3BHK apartment in Gachibowli, close to financial district and reputed schools.',
         25000, 'Gachibowli, Hyderabad', 'Apartment', 'Rent', 3, 2, 1550,
         'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80',
         'Parking, Security, Power Backup, Lift, Play Area'),

        (2, '3BHK Villa in Kokapet',
         'Modern 3BHK villa with a small private garden in Kokapet, the new growth corridor of Hyderabad. Easy access to financial district.',
         18000000, 'Kokapet, Hyderabad', 'Villa', 'Sale', 3, 3, 2400,
         'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80',
         'Private Garden, Parking, Security, Club Access, Swimming Pool'),

        (2, '2BHK Apartment in Manikonda',
         'Budget-friendly 2BHK apartment in Manikonda, close to Mindspace and Raheja Mindspace IT Park.',
         15000, 'Manikonda, Hyderabad', 'Apartment', 'Rent', 2, 2, 1100,
         'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80',
         'Parking, Security, Gym, Power Backup'),

        # ─── CHENNAI ─────────────────────────────────────────────────────────
        (2, '2BHK Apartment on OMR',
         'Modern 2BHK apartment on Old Mahabalipuram Road in a secure gated community. Great connectivity to IT corridors and ECR Beach.',
         5800000, 'Old Mahabalipuram Road, Chennai', 'Apartment', 'Sale', 2, 2, 1100,
         'https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800&q=80',
         'Gym, Swimming Pool, Parking, Security, Lift'),

        (2, 'Traditional House in Adyar',
         'Charming and spacious traditional 3BHK house in sought-after Adyar. Close to Adyar River and top educational institutions.',
         28000, 'Adyar, Chennai', 'House', 'Rent', 3, 2, 1900,
         'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80',
         'Garden, Parking, Security, Pooja Room, Bore Well'),

        (2, '3BHK Apartment in Anna Nagar',
         'Spacious 3BHK apartment in the prime Anna Nagar locality. Close to Anna Nagar Tower and all commercial establishments.',
         8900000, 'Anna Nagar, Chennai', 'Apartment', 'Sale', 3, 2, 1500,
         'https://images.unsplash.com/photo-1416331108676-a22ccb276e35?w=800&q=80',
         'Gym, Covered Parking, Security, Lift, Community Hall'),

        (2, '2BHK Flat in Perambur',
         'Affordable 2BHK flat in Perambur, close to Perambur railway station and major bus routes.',
         10000, 'Perambur, Chennai', 'Apartment', 'Rent', 2, 1, 950,
         'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=800&q=80',
         'Parking, Security, Power Backup'),

        (2, 'Luxury Villa in ECR',
         'Breathtaking beachside luxury villa on the East Coast Road with private beach access and infinity pool.',
         90000000, 'East Coast Road (ECR), Chennai', 'Villa', 'Sale', 5, 5, 6000,
         'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',
         'Private Beach, Infinity Pool, Home Theatre, Smart Home, Garage'),

        # ─── PUNE ────────────────────────────────────────────────────────────
        (2, '2BHK Apartment in Hinjewadi',
         'Brand new 2BHK apartment in Hinjewadi Phase 1, the IT hub of Pune. Just 2 km from Rajiv Gandhi Infotech Park.',
         7200000, 'Hinjewadi, Pune', 'Apartment', 'Sale', 2, 2, 1150,
         'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&q=80',
         'Gym, Swimming Pool, Parking, Landscaped Garden, Security'),

        (2, 'Bungalow in Koregaon Park',
         'Elegant 4BHK bungalow in the green and upscale Koregaon Park. Close to international schools, restaurants, and Osho Ashram.',
         55000000, 'Koregaon Park, Pune', 'Villa', 'Sale', 4, 4, 4200,
         'https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=800&q=80',
         'Garden, Private Pool, Garage, Staff Quarter, Home Automation'),

        (2, '3BHK Flat in Wakad',
         'Modern 3BHK apartment in Wakad, close to the Mumbai-Pune Expressway. Excellent for professionals commuting to Mumbai.',
         20000, 'Wakad, Pune', 'Apartment', 'Rent', 3, 2, 1400,
         'https://images.unsplash.com/photo-1560185127-6a8f94d94deb?w=800&q=80',
         'Gym, Swimming Pool, Parking, Security, Club House'),

        (2, '1BHK Flat in Kothrud',
         'Budget 1BHK flat in Kothrud, perfect for students near Symbiosis and other colleges.',
         8500, 'Kothrud, Pune', 'Apartment', 'Rent', 1, 1, 550,
         'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80',
         'Security, Water 24/7, Power Backup'),

        (2, '2BHK Apartment in Aundh',
         'Well-located 2BHK apartment in Aundh near Pune University. Close to D-Mart, restaurants, and IT companies.',
         6800000, 'Aundh, Pune', 'Apartment', 'Sale', 2, 2, 1100,
         'https://images.unsplash.com/photo-1504615755583-2916b52192a3?w=800&q=80',
         'Parking, Security, Gym, Power Backup, Children Play Area'),

        # ─── KOLKATA ─────────────────────────────────────────────────────────
        (2, '3BHK Apartment in New Town',
         'Spacious 3BHK in the well-planned New Town area of Kolkata. Close to Eco Park and IT companies at Sector V.',
         5500000, 'New Town, Kolkata', 'Apartment', 'Sale', 3, 2, 1600,
         'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80',
         'Gym, Swimming Pool, Parking, Security, Park'),

        (2, 'Heritage House in South Kolkata',
         'Charming 4BHK heritage-style house in the quiet lanes of Ballygunge. Old-world charm with modern renovations.',
         35000000, 'Ballygunge, Kolkata', 'House', 'Sale', 4, 3, 3000,
         'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80',
         'Garden, Servant Quarter, Parking, Terrace'),

        (2, '2BHK Flat in Salt Lake City',
         'Well-maintained 2BHK apartment in Salt Lake Sector III, close to offices, schools, and shopping centres.',
         12000, 'Salt Lake City, Kolkata', 'Apartment', 'Rent', 2, 2, 1100,
         'https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800&q=80',
         'Parking, Security, Lift, Power Backup'),

        # ─── AHMEDABAD ───────────────────────────────────────────────────────
        (2, '3BHK Apartment in SG Highway',
         'Modern 3BHK apartment on Sarkhej-Gandhinagar Highway in a premium gated society with world-class amenities.',
         8200000, 'SG Highway, Ahmedabad', 'Apartment', 'Sale', 3, 3, 1700,
         'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&q=80',
         'Gym, Swimming Pool, Parking, Squash Court, Clubhouse'),

        (2, '2BHK Flat in Bopal',
         'Budget-friendly 2BHK flat in Bopal, the fastest growing suburb of Ahmedabad. Close to new metro corridor.',
         12000, 'Bopal, Ahmedabad', 'Apartment', 'Rent', 2, 2, 1050,
         'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80',
         'Parking, Security, Power Backup, Lift'),

        (2, '4BHK Villa in Prahlad Nagar',
         'Luxurious 4BHK villa in Prahlad Nagar corporate road area. Close to top malls, schools and hospitals.',
         30000000, 'Prahlad Nagar, Ahmedabad', 'Villa', 'Sale', 4, 4, 4000,
         'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',
         'Private Pool, Landscaped Garden, Modular Kitchen, Smart Home, Garage'),

        # ─── JAIPUR ──────────────────────────────────────────────────────────
        (2, '3BHK Flat in Vaishali Nagar',
         'Premium 3BHK flat in Vaishali Nagar, one of Jaipur\'s posh localities. Close to World Trade Park and schools.',
         6500000, 'Vaishali Nagar, Jaipur', 'Apartment', 'Sale', 3, 2, 1500,
         'https://images.unsplash.com/photo-1416331108676-a22ccb276e35?w=800&q=80',
         'Gym, Security, Parking, Lift, Community Hall'),

        (2, 'Royal Haveli Style House in Civil Lines',
         'Majestic 5BHK traditional Rajasthani-style house in Civil Lines with intricate design, courtyard and terrace garden.',
         45000000, 'Civil Lines, Jaipur', 'Villa', 'Sale', 5, 4, 5000,
         'https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=800&q=80',
         'Courtyard, Rooftop Garden, Parking, Staff Quarter, Traditional Architecture'),

        (2, '2BHK Flat in Malviya Nagar Jaipur',
         'Affordable and well-located 2BHK in Malviya Nagar. Close to Jaipuria Mall, schools and metro corridor.',
         10000, 'Malviya Nagar, Jaipur', 'Apartment', 'Rent', 2, 1, 1000,
         'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80',
         'Parking, Security, Power Backup'),

        # ─── KOCHI ───────────────────────────────────────────────────────────
        (2, '3BHK Apartment in Marine Drive Kochi',
         'Stunning 3BHK apartment with backwater views on Marine Drive in Ernakulam. Premium location in the heart of Kochi.',
         12000000, 'Marine Drive, Kochi', 'Apartment', 'Sale', 3, 3, 1650,
         'https://images.unsplash.com/photo-1504615755583-2916b52192a3?w=800&q=80',
         'Gym, Swimming Pool, Parking, Security, Backwater View'),

        (2, '2BHK House in Kakkanad',
         'Modern 2BHK independent house in Kakkanad IT zone. Close to Infopark and Smart City Kochi.',
         18000, 'Kakkanad, Kochi', 'House', 'Rent', 2, 2, 1200,
         'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80',
         'Garden, Parking, Security, Bore Well'),

        # ─── CHANDIGARH ──────────────────────────────────────────────────────
        (2, '3BHK Flat in Sector 20 Chandigarh',
         'Spacious 3BHK flat in the well-planned Sector 20. Chandigarh\'s green sectors provide unmatched quality of life.',
         9500000, 'Sector 20, Chandigarh', 'Apartment', 'Sale', 3, 2, 1700,
         'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80',
         'Gym, Security, Parking, Park Access, Community Hall'),

        (2, '2BHK House in Panchkula',
         'Independent 2BHK house in Panchkula Sector 9, close to Chandigarh. Quiet residential locality with parks and schools nearby.',
         22000000, 'Sector 9, Panchkula', 'House', 'Sale', 2, 2, 1400,
         'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80',
         'Garden, Parking, Bore Well, Security'),

        # ─── INDORE ──────────────────────────────────────────────────────────
        (2, '2BHK Apartment in Vijay Nagar Indore',
         'Nicely built 2BHK apartment in Vijay Nagar, one of the most happening areas of Indore. Close to C21 Mall and Treasure Island.',
         4500000, 'Vijay Nagar, Indore', 'Apartment', 'Sale', 2, 2, 1050,
         'https://images.unsplash.com/photo-1560185127-6a8f94d94deb?w=800&q=80',
         'Parking, Security, Lift, Power Backup'),

        (2, '3BHK House in Super Corridor',
         'Modern 3BHK house in Super Corridor, the upcoming IT hub of Indore. Excellent infrastructure and upcoming metro line.',
         8500, 'Super Corridor, Indore', 'House', 'Rent', 3, 2, 1600,
         'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&q=80',
         'Garden, Parking, Security, Power Backup'),

        # ─── SURAT ───────────────────────────────────────────────────────────
        (2, '3BHK Apartment in Vesu Surat',
         'Upscale 3BHK apartment in Vesu, Surat\'s most affluent area. Premium complex with international-level amenities.',
         7500000, 'Vesu, Surat', 'Apartment', 'Sale', 3, 3, 1600,
         'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&q=80',
         'Gym, Swimming Pool, Parking, Clubhouse, Security'),

        (2, '2BHK Flat in Adajan Surat',
         'Affordable 2BHK flat in Adajan near the river front. Easy access to Diamond market and textile hubs.',
         11000, 'Adajan, Surat', 'Apartment', 'Rent', 2, 1, 1000,
         'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80',
         'Parking, Security, Power Backup, Lift'),

        # ─── LUCKNOW ─────────────────────────────────────────────────────────
        (2, '3BHK Apartment in Gomti Nagar',
         'Premium 3BHK apartment in Gomti Nagar, the most prestigious area of Lucknow. Close to Sahara Ganj Mall and Vidhan Sabha.',
         7000000, 'Gomti Nagar, Lucknow', 'Apartment', 'Sale', 3, 2, 1550,
         'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80',
         'Gym, Security, Parking, Club House, Swimming Pool'),

        (2, '4BHK Kothi in Hazratganj',
         'Majestic 4BHK kothi in the historic and central Hazratganj area of Lucknow. Massive rooms, large lawn, and premium construction.',
         38000000, 'Hazratganj, Lucknow', 'House', 'Sale', 4, 3, 3200,
         'https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800&q=80',
         'Lawn, Parking, Servant Quarter, Generator, Security'),

    ]

    cursor.executemany("""
    INSERT INTO properties (agent_id, title, description, price, location, property_type, status, bedrooms, bathrooms, area, image_url, amenities)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, properties)

    conn.commit()
    conn.close()
    print(f"Database initialized successfully with {len(properties)} properties!")

if __name__ == '__main__':
    init_db()
