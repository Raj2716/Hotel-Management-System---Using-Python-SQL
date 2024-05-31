import mysql.connector
from mysql.connector import Error

# Connect to MySQL database
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3307,
            database='hotel_management',
            user='root',  # replace with your MySQL username
            password='1234'  # replace with your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Database Connection Error:", e)
        return None

# Close the database connection
def close_connection(connection):
    if connection.is_connected():
        connection.close()

class Hotel:
    def __init__(self, name, location, ratings, available_rooms, price, amenities, bed_type):
        self.name = name
        self.location = location
        self.ratings = ratings
        self.available_rooms = available_rooms
        self.price = price
        self.amenities = amenities
        self.bed_type = bed_type

class User:
    def __init__(self, name, mobile_number, check_in, check_out, location, price, num_members, category, preferences):
        self.name = name
        self.mobile_number = mobile_number
        self.check_in = check_in
        self.check_out = check_out
        self.location = location
        self.price = price
        self.num_members = num_members
        self.category = category
        self.preferences = preferences

def register_user():
    name = input("Enter your name: ")
    username = input("Choose a username: ")
    password = input("Choose a password: ")
    mobile_number = input("Enter your mobile number: ")

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        sql = "INSERT INTO users (name, username, password, mobile_number) VALUES (%s, %s, %s, %s)"
        val = (name, username, password, mobile_number)
        cursor.execute(sql, val)
        connection.commit()
        close_connection(connection)
        print("User registered successfully!")

def register_hotelier():
    name = input("Enter your name: ")
    username = input("Choose a username: ")
    password = input("Choose a password: ")

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        sql = "INSERT INTO hoteliers (name, username, password) VALUES (%s, %s, %s)"
        val = (name, username, password)
        cursor.execute(sql, val)
        connection.commit()
        close_connection(connection)
        print("Hotelier registered successfully!")

def hotelier_login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM hoteliers WHERE username = %s AND password = %s", (username, password))
        hotelier = cursor.fetchone()
        close_connection(connection)
        if hotelier:
            print("Hotelier logged in successfully!")
            while True:
                print("1. Add Hotel")
                print("2. View Bookings")
                print("3. Logout")
                choice = input("Enter your choice: ")
                if choice == '1':
                    add_hotel(hotelier[0])  # Pass hotelier's ID
                elif choice == '2':
                    view_bookings(hotelier[0])  # Pass hotelier's ID
                elif choice == '3':
                    break
                else:
                    print("Invalid choice! Please try again.")
        else:
            print("Invalid credentials!")

def user_login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        close_connection(connection)
        if user:
            print("User logged in successfully!")
            search_hotels(user)
        else:
            print("Invalid credentials!")

def add_hotel(hotelier_id):
    name = input("Enter hotel name: ")
    location = input("Enter hotel location: ")
    price = float(input("Enter price per night: "))
    amenities = input("Enter amenities (comma separated): ")
    ratings = float(input("Enter hotel ratings (out of 5): "))
    available_rooms = int(input("Enter number of available rooms: "))
    bed_type = input("Enter bed type (single, double, king, etc.): ")

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        sql = "INSERT INTO hotels (name, location, ratings, available_rooms, price, amenities, bed_type, hotelier_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (name, location, ratings, available_rooms, price, amenities, bed_type, hotelier_id)
        cursor.execute(sql, val)
        connection.commit()
        close_connection(connection)
        print("Hotel added successfully!")

def search_hotels(user):
    location = input("Enter preferred location: ")
    max_price = float(input("Enter maximum price per night: "))
    preferences = input("Enter preferences (comma separated): ").split(',')

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM hotels WHERE location = %s AND price <= %s AND available_rooms > 0",
                       (location, max_price))
        hotels = cursor.fetchall()
        close_connection(connection)

        found_hotels = []
        for hotel in hotels:
            if set(preferences).issubset(set(hotel['amenities'].split(','))):
                found_hotels.append(hotel)

        if found_hotels:
            print("Search Results:")
            for hotel in found_hotels:
                print(f"Hotel Name: {hotel['name']}")
                print(f"Location: {hotel['location']}")
                print(f"Ratings: {hotel['ratings']}")
                print(f"Available Rooms: {hotel['available_rooms']}")
                print(f"Price: {hotel['price']}")
                print(f"Amenities: {hotel['amenities']}")
                print(f"Bed Type: {hotel['bed_type']}")
                print("-" * 50)

            book_hotel(user, found_hotels)
        else:
            print("No hotels found matching your criteria.")
    else:
        print("Failed to connect to the database.")

def book_hotel(user, hotels):
    hotel_name = input("Enter the name of the hotel you want to book: ")
    selected_hotel = next((hotel for hotel in hotels if hotel['name'] == hotel_name), None)

    if selected_hotel:
        check_in = input("Enter check-in date (YYYY-MM-DD): ")
        check_out = input("Enter check-out date (YYYY-MM-DD): ")
        num_members = int(input("Enter number of members: "))

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            sql = "INSERT INTO bookings (user_id, hotel_id, check_in, check_out, num_members) VALUES (%s, %s, %s, %s, %s)"
            val = (user[0], selected_hotel['id'], check_in, check_out, num_members)
            cursor.execute(sql, val)
            cursor.execute("UPDATE hotels SET available_rooms = available_rooms - 1 WHERE id = %s", (selected_hotel['id'],))
            connection.commit()
            close_connection(connection)
            print("Hotel booked successfully!")
    else:
        print("Invalid hotel name.")

def view_bookings(hotelier_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor(dictionary=True)
        sql = """
        SELECT u.name as user_name, u.mobile_number, b.check_in, b.check_out, b.num_members, h.name as hotel_name,h.amenities,h.location
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN hotels h ON b.hotel_id = h.id
        WHERE h.hotelier_id = %s
        """
        cursor.execute(sql, (hotelier_id,))
        bookings = cursor.fetchall()
        close_connection(connection)

        if bookings:
            print("Bookings:")
            for booking in bookings:
                print(f"User Name: {booking['user_name']}")
                print(f"Mobile Number: {booking['mobile_number']}")
                print(f"Location: {booking['location']}")
                print(f"Amenities Chosen: {booking['amenities']}")
                print(f"Check-in Date: {booking['check_in']}")
                print(f"Check-out Date: {booking['check_out']}")
                print(f"Number of Members: {booking['num_members']}")
                print(f"Hotel Name: {booking['hotel_name']}")
                print("-" * 50)
        else:
            print("No bookings found for your hotels.")
    else:
        print("Failed to connect to the database.")
def main():
    while True:
        print("Welcome to Hotel Management System")
        print("1. Register as User")
        print("2. Register as Hotelier")
        print("3. User Login")
        print("4. Hotelier Login")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            register_hotelier()
        elif choice == '3':
            user_login()
        elif choice == '4':
            hotelier_login()
        elif choice == '5':
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
