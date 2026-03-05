import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('gurukul.db')
        cursor = conn.cursor()
        
        print("=== User Records (@demo.com) ===")
        cursor.execute("SELECT email, role, tenant_id FROM users WHERE email LIKE '%@demo.com'")
        users = cursor.fetchall()
        for user in users:
            print(user)
            
        print("\n=== Demo Account Counts Per Tenant ===")
        cursor.execute("SELECT tenant_id, COUNT(*) FROM users WHERE email IN ('admin@demo.com', 'teacher@demo.com', 'parent@demo.com', 'student@demo.com') GROUP BY tenant_id")
        counts = cursor.fetchall()
        for count in counts:
            print(count)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
