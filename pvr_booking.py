import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('pvr_booking.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS Movies (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL UNIQUE)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Shows (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  movie_id INTEGER,
                  timing TEXT,
                  seats INTEGER,
                  available_seats INTEGER,
                  FOREIGN KEY (movie_id) REFERENCES Movies(id))''')

conn.commit()

inbuilt_movies = [
    ("Avengers", [("10:00 AM", 50), ("1:00 PM", 50), ("4:00 PM", 50)]),
    ("Minions", [("11:00 AM", 50), ("2:00 PM", 50), ("5:00 PM", 50)]),
    ("Pulp Fiction", [("12:00 PM", 50), ("3:00 PM", 50), ("6:00 PM", 50)]),
    ("Rockstar", [("9:00 AM", 50), ("12:00 PM", 50), ("3:00 PM", 50)])
]

# Remove duplicate movies
cursor.execute("DELETE FROM Movies WHERE id NOT IN (SELECT MIN(id) FROM Movies GROUP BY title)")
conn.commit()

# Function to check if a movie already exists
def movie_exists(title):
    cursor.execute("SELECT id FROM Movies WHERE title=?", (title,))
    return cursor.fetchone()

# Insert movies and shows only if they don't already exist
for movie, shows in inbuilt_movies:
    if not movie_exists(movie):
        cursor.execute("INSERT INTO Movies (title) VALUES (?)", (movie,))
        movie_id = cursor.lastrowid
        for timing, seats in shows:
            cursor.execute("INSERT INTO Shows (movie_id, timing, seats, available_seats) VALUES (?, ?, ?, ?)",
                           (movie_id, timing, seats, seats))

conn.commit()

def display_movies():
    cursor.execute("SELECT * FROM Movies")
    movies = cursor.fetchall()
    print("Movies:")
    for movie in movies:
        print(f"{movie[0]}. {movie[1]}")
    return movies

def display_shows(movie_id):
    cursor.execute("SELECT * FROM Shows WHERE movie_id=?", (movie_id,))
    shows = cursor.fetchall()
    print(f"Shows for Movie ID {movie_id}:")
    for show in shows:
        print(f"{show[0]}. Timing: {show[2]}, Seats: {show[3]}, Available Seats: {show[4]}")
    return shows

def book_seats(show_id, num_seats):
    cursor.execute("SELECT available_seats FROM Shows WHERE id=?", (show_id,))
    available_seats = cursor.fetchone()[0]
    if available_seats >= num_seats:
        cursor.execute("UPDATE Shows SET available_seats=? WHERE id=?",
                       (available_seats - num_seats, show_id))
        conn.commit()
        print(f'Successfully booked {num_seats} seats for Show ID {show_id}.')
    else:
        print(f'Not enough available seats. Only {available_seats} seats are available.')

def cancel_seats(show_id, num_seats):
    cursor.execute("SELECT available_seats, seats FROM Shows WHERE id=?", (show_id,))
    available_seats, total_seats = cursor.fetchone()
    if total_seats - available_seats >= num_seats:
        cursor.execute("UPDATE Shows SET available_seats=? WHERE id=?",
                       (available_seats + num_seats, show_id))
        conn.commit()
        print(f'Successfully cancelled {num_seats} seats for Show ID {show_id}.')
    else:
        print(f'Cannot cancel {num_seats} seats. Only {total_seats - available_seats} seats are booked.')

# User Interface
while True:
    print("\nPVR Booking System")
    print("1. Display Movies")
    print("2. Display Shows for a Movie")
    print("3. Book Seats")
    print("4. Cancel Seats")
    print("5. Exit")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        display_movies()
    elif choice == 2:
        movies = display_movies()
        movie_id = int(input("Enter movie ID to display shows: "))
        if any(movie[0] == movie_id for movie in movies):
            display_shows(movie_id)
        else:
            print("Invalid movie ID.")
    elif choice == 3:
        movies = display_movies()
        movie_id = int(input("Enter movie ID to book seats: "))
        if any(movie[0] == movie_id for movie in movies):
            shows = display_shows(movie_id)
            show_id = int(input("Enter show ID to book seats: "))
            if any(show[0] == show_id for show in shows):
                num_seats = int(input("Enter number of seats to book: "))
                book_seats(show_id, num_seats)
            else:
                print("Invalid show ID.")
        else:
            print("Invalid movie ID.")
    elif choice == 4:
        movies = display_movies()
        movie_id = int(input("Enter movie ID to cancel seats: "))
        if any(movie[0] == movie_id for movie in movies):
            shows = display_shows(movie_id)
            show_id = int(input("Enter show ID to cancel seats: "))
            if any(show[0] == show_id for show in shows):
                num_seats = int(input("Enter number of seats to cancel: "))
                cancel_seats(show_id, num_seats)
            else:
                print("Invalid show ID.")
        else:
            print("Invalid movie ID.")
    elif choice == 5:
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please try again.")

conn.close()
