"""
Seed Script — Create default admin, sample officer, and incident categories.
Run after executing schema.sql:
    python seed.py
"""
from werkzeug.security import generate_password_hash
from database import execute, fetch_one


def seed():
    print("Seeding database...")

    # ── Default Admin ──────────────────────────────────────────
    admin = fetch_one("SELECT id FROM users WHERE email = %s", ('admin@portal.com',))
    if not admin:
        admin_id = execute(
            """INSERT INTO users (full_name, email, phone, password_hash, role)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                'System Administrator',
                'admin@portal.com',
                '+91 9000000000',
                generate_password_hash('Admin@123', method='pbkdf2:sha256'),
                'admin'
            )
        )
        print(f"  [OK] Admin created: admin@portal.com / Admin@123  (ID: {admin_id})")
    else:
        print("  [SKIP] Admin already exists.")

    # ── Default Officer ────────────────────────────────────────
    officer = fetch_one("SELECT id FROM users WHERE email = %s", ('officer@portal.com',))
    if not officer:
        officer_user_id = execute(
            """INSERT INTO users (full_name, email, phone, password_hash, role)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                'Inspector Sharma',
                'officer@portal.com',
                '+91 9000000001',
                generate_password_hash('Officer@123', method='pbkdf2:sha256'),
                'officer'
            )
        )
        execute(
            """INSERT INTO officers (user_id, badge_number, department, specialization)
               VALUES (%s, %s, %s, %s)""",
            (officer_user_id, 'CYB-001', 'Cyber Crime Unit', 'Online Fraud')
        )
        print(f"  [OK] Officer created: officer@portal.com / Officer@123  (ID: {officer_user_id})")
    else:
        print("  [SKIP] Officer already exists.")

    # ── Incident Categories ────────────────────────────────────
    categories = [
        ('Phishing', 'Fraudulent attempts to obtain sensitive information via email, SMS, or fake websites.'),
        ('Ransomware', 'Malicious software that encrypts files and demands payment for decryption.'),
        ('Identity Theft', 'Unauthorized use of personal information for fraudulent purposes.'),
        ('Online Fraud', 'Financial scams conducted through digital channels.'),
        ('Cyberbullying', 'Harassment, threats, or intimidation through digital platforms.'),
        ('Data Breach', 'Unauthorized access to confidential or protected data.'),
        ('Hacking', 'Unauthorized intrusion into computer systems or networks.'),
        ('Malware', 'Infection by viruses, trojans, worms, or spyware.'),
        ('Social Engineering', 'Manipulation tactics to trick people into revealing information.'),
        ('Denial of Service', 'Attacks that disrupt the availability of online services.'),
        ('Child Exploitation', 'Online abuse or exploitation of minors.'),
        ('Intellectual Property Theft', 'Unauthorized copying or distribution of copyrighted content.'),
    ]

    for name, desc in categories:
        existing = fetch_one(
            "SELECT id FROM incident_categories WHERE name = %s", (name,)
        )
        if not existing:
            execute(
                "INSERT INTO incident_categories (name, description) VALUES (%s, %s)",
                (name, desc)
            )

    print(f"  [OK] {len(categories)} incident categories ensured.")
    print("\nSeeding complete!")
    print("   Admin  -> admin@portal.com / Admin@123")
    print("   Officer -> officer@portal.com / Officer@123")


if __name__ == '__main__':
    seed()
