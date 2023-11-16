import psycopg, re, datetime
from psycopg.rows import dict_row

DATABASE_QUERY_STRING = """
                        CREATE TABLE users (
                            user_id VARCHAR(255) PRIMARY KEY,
                            password BIGINT NOT NULL,
                            first_name VARCHAR(255) NOT NULL,
                            last_name VARCHAR(255) NOT NULL,
                            has_email BOOLEAN DEFAULT TRUE,
                            has_sms BOOLEAN DEFAULT TRUE,
                            has_ad BOOLEAN DEFAULT TRUE,
                            language VARCHAR(255) DEFAULT 'English',
                            university VARCHAR(255),
                            major VARCHAR(255),
                            tier VARCHAR(255) DEFAULT 'Standard',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                            last_login TIMESTAMP
                        );

                        CREATE TABLE jobs (
                            job_id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) REFERENCES users(user_id),
                            title VARCHAR(255) NOT NULL,
                            description TEXT,
                            employer VARCHAR(255) NOT NULL,
                            location VARCHAR(255) NOT NULL,
                            salary DECIMAL,
                            first_name VARCHAR(255),
                            last_name VARCHAR(255),
                            date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE friendships (
                            friendship_id SERIAL PRIMARY KEY,
                            student1_id VARCHAR(255) REFERENCES users(user_id),
                            student2_id VARCHAR(255) REFERENCES users(user_id),
                            status TEXT CHECK (status IN ('pending', 'confirmed'))
                        );
                        
                        CREATE TABLE profiles (
                            profile_id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) REFERENCES users(user_id),
                            title TEXT,
                            about TEXT
                        );

                        CREATE TABLE experiences (
                            experience_id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) REFERENCES users(user_id),
                            title VARCHAR(255),
                            employer VARCHAR(255),
                            date_started DATE,
                            date_ended DATE,
                            location VARCHAR(255),
                            description TEXT
                        );

                        CREATE TABLE educations (
                            education_id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) REFERENCES users(user_id),
                            school_name VARCHAR(255),
                            degree VARCHAR(255),
                            year_started INT,
                            year_ended INT
                        );

                        CREATE TABLE job_applications (
                            application_id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) REFERENCES users(user_id),
                            job_id INT REFERENCES jobs(job_id) ON DELETE CASCADE,
                            title VARCHAR(255),
                            graduation_date DATE,
                            start_date DATE,
                            paragraph_text TEXT,
                            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE (user_id, job_id)
                        );

                        CREATE TABLE messages (
                            message_id SERIAL PRIMARY KEY,
                            sender VARCHAR(255) REFERENCES users(user_id),
                            receiver VARCHAR(255) REFERENCES users(user_id),
                            message_txt TEXT,
                            status TEXT CHECK (status IN ('unread', 'read')),
                            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE saved_jobs (
                            user_id VARCHAR(255) REFERENCES users(user_id),
                            job_id INT REFERENCES jobs(job_id) ON DELETE CASCADE,
                            PRIMARY KEY (user_id, job_id),
                            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        """

def createDatabase(databaseUser, databasePassword, databaseName, databaseHost, databasePort, databaseQueryString=DATABASE_QUERY_STRING):
    with psycopg.connect(user=databaseUser, password=databasePassword) as connection:
        connection._set_autocommit(True)
        with connection.cursor() as cursor:
            cursor.execute(f"""CREATE DATABASE {databaseName};""")
    with psycopg.connect(dbname=databaseName, user=databaseUser, password=databasePassword, host=databaseHost, port=databasePort) as connection:
        with connection.cursor() as cursor:
            cursor.execute(databaseQueryString)

def getDate():
    while True:
        year = input('Enter year: ')
        if year.isnumeric():
            year = int(year)
            if year <= 9999 and year >= 1:
                break
        print('Invalid input. Please input a valid year.')

    while True:
        month = input('Enter month: ')
        if month.isnumeric():
            month = int(month)
            if month <= 12 and month >= 1:
                break
        print('Invalid input. Please input a valid month.')

    if month == 2:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            max = 29
        else:
            max = 28
    elif month in (1, 3, 5, 7, 8, 10, 12):
        max = 31
    else:
        max = 30

    while True:
        day = input('Enter day: ')
        if day.isnumeric():
            day = int(day)
            if day <= max and day >= 1:
                break
        print('Invalid input. Please input a valid day.')

    return f"{year}-{month}-{day}"

class InCollegeBackend():

    ######################
    ## INPUT VALIDATION ##
    ######################

    def validUser(self, UserID):
        """
        Checks if the provided UserID is unique
        Check if the provided password meets certain requirements
        """
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                search_query = f"""
                SELECT user_id
                FROM users
                WHERE user_id = %s;
                """
                cursor.execute(search_query, (UserID,))
                users = cursor.fetchall()

                if users:
                    return False
        return True

    def validPassword(self, password):
        if not (8 <= len(password) <= 12):
            return False
        # Check if the password contains at least one capital letter
        if not re.search(r'[A-Z]', password):
            return False
        # Check if the password contains at least one digit
        if not re.search(r'\d', password):
            return False
        # Check if the password contains at least one special character (non-alphanumeric)
        if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]', password):
            return False
        return True

    def completeRow(self, table, crit=[]):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:

                query = f"""SELECT *
                            FROM {table}
                            WHERE user_id = '{self.userID}'
                            """

                if crit:
                    i = 0
                    while i < len(crit)-1:
                        query = query + f""" AND {crit[i]} = {crit[i+1]}"""
                        i = i+2

                query = query + ';'
                cursor.execute(query)
                vals = cursor.fetchall()

                if not vals:
                    return False

                vals = vals[0]

                if None in vals:
                    return False

                return True

    ###########
    ## USERS ##
    ###########

    # change crit/crit2 method to accept a list of lists with critical rows and critical entries?
    def changeEntry(self, table, column, entry, crit="", crit2=""):

        # Update class attributes
        if column in ["has_email", "has_sms", "has_ad", "language"]:
            setattr(self, column, entry)

        # Connect to the database and execute the UPDATE statement
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Update the user's preference in the database
                update_query = f"""
                UPDATE {table} SET {column} = %s WHERE user_id = %s
                """
                if crit and crit2:
                    update_query = update_query + \
                        f""" AND {crit} = {str(crit2)}"""
                update_query = update_query + ';'
                cursor.execute(update_query, (entry, self.userID))

    def getUserName(self, user_id):
        # Get the name of a user based on their user ID
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD,
                             host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT first_name, last_name
                FROM users
                WHERE user_id = %s;
                """
                cursor.execute(fetch_query, (user_id,))
                user = cursor.fetchone()

        if user:
            first_name, last_name = user
            return f"{first_name} {last_name}"
        else:
            return "Unknown User"

    def getUserCount(self):
        try:
            with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    # Get the number of users in the database
                    cursor.execute("SELECT COUNT(*) FROM users;")
                    user_count = cursor.fetchone()[0]
            return user_count
        except Exception as e:
            print(f"An error occurred: {e}")

    def writeUser(self, userID, password, first, last, has_email, has_sms, has_ad, university, major, tier):
        now = datetime.datetime.now()
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Insert Data into users table
                insert_query = """
                INSERT INTO users (user_id, password, first_name, last_name, has_email, has_sms, has_ad, university, major, tier, created_at, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (userID, password, first, last,
                               has_email, has_sms, has_ad, university, major, tier, now, now))

    def signInHelper(self, userID, password):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                # Fetch user details from the database
                cursor.execute(
                    "SELECT * FROM users WHERE user_id = %s AND password = %s", (userID, password))
                user = cursor.fetchone()
        return user

    def getUserByCriteria(self, criteria, entry):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                search_query = f"""
                SELECT user_id, first_name, last_name, university, major 
                FROM users 
                WHERE {criteria} = %s AND user_id != %s;
                """
                cursor.execute(search_query, (entry, self.userID))

                users = cursor.fetchall()
        return users

    def getAllUsers(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Construct the query
                fetch_query = f"""
                SELECT user_id, first_name, last_name 
                FROM users; 
                """
                cursor.execute(fetch_query)
                return cursor.fetchall()

    ##########
    ## JOBS ##
    ##########

    def listJobs(self):
        """
        Retrieve a list of all available jobs.
        """
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute("SELECT * FROM jobs")
                jobs = cursor.fetchall()
        return jobs
    
    def hasAppliedForJob(self, job_id):
        """
        Check if the user has already applied for a job.
        """
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM job_applications WHERE user_id = %s AND job_id = %s", (self.userID, job_id))
                return cursor.fetchone() is not None
            
    def jobPostedBySelf(self, job_id):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM jobs WHERE job_id = %s", (job_id,))
                job_user_id = cursor.fetchone()
                if job_user_id and job_user_id[0] == self.userID:
                    return True
                return False
    
    def getJobTitle(self, job_id):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT title FROM jobs WHERE job_id = %s", (job_id,))
                return cursor.fetchone()[0]

    def storeJobApplication(self, job_id, job_title, graduation_date, start_date, paragraph_text):
        """
        Store the job application in the database.
        """
        now = datetime.datetime.now()
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO job_applications (user_id, job_id, title, graduation_date, start_date, paragraph_text, applied_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (self.userID, job_id, job_title, graduation_date, start_date, paragraph_text, now)
                )

    def listAppliedJobs(self):
        """
        Print a list of jobs that the user has applied for.
        """
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    "SELECT jobs.* FROM jobs INNER JOIN job_applications ON jobs.job_id = job_applications.job_id WHERE job_applications.user_id = %s", (self.userID,))
                applied_jobs = cursor.fetchall()

        if not applied_jobs:
            print("You haven't applied for any jobs yet.")
        else:
            print("\nJobs Applied For:")
            for job in applied_jobs:
                print(f"- Title: {job['title']}")
                print(f"  Description: {job['description']}")
                print(f"  Employer: {job['employer']}")
                print(f"  Location: {job['location']}")
                print(f"  Salary: {job['salary']}\n")

    def listUnappliedJobs(self):
        """
        Print a list of jobs that the user has not yet applied for.
        """
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    "SELECT * FROM jobs WHERE job_id NOT IN (SELECT job_id FROM job_applications WHERE user_id = %s)", (self.userID,))
                unapplied_jobs = cursor.fetchall()

        if not unapplied_jobs:
            print("You've applied for all available jobs.")
        else:
            print("\nJobs Not Yet Applied For:")
            for job in unapplied_jobs:
                print(f"- Title: {job['title']}")
                print(f"  Description: {job['description']}")
                print(f"  Employer: {job['employer']}")
                print(f"  Location: {job['location']}")
                print(f"  Salary: {job['salary']}\n")

    def hasSavedJob(self, job_id):
        """
        Check if the user has already saved a job.
        """
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM saved_jobs WHERE user_id = %s AND job_id = %s", (self.userID, job_id))
                return cursor.fetchone() is not None

    def saveJobToDatabase(self, job_id):
        """
        Save the job to the user's saved jobs list in the database.
        """
        if self.hasSavedJob(job_id):
            print("Job successfully unsaved")
            with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    # First, delete any existing saved job with the same job_id
                    cursor.execute(
                        "DELETE FROM saved_jobs WHERE user_id = %s AND job_id = %s",
                        (self.userID, job_id)
                    )
        else:
            print("Job successfully saved")
            now = datetime.datetime.now()
            with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO saved_jobs (user_id, job_id, saved_at) VALUES (%s, %s, %s)",
                        (self.userID, job_id, now)
                    )

    def listSavedJobs(self):
        """
        Print a list of jobs that the user has saved.
        """
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute("""
                    SELECT jobs.* 
                    FROM jobs
                    INNER JOIN saved_jobs ON jobs.job_id = saved_jobs.job_id
                    WHERE saved_jobs.user_id = %s
                """, (self.userID,))
                saved_jobs = cursor.fetchall()

        if not saved_jobs:
            print("You haven't saved any jobs yet.")
        else:
            print("\nSaved Jobs:")
            for job in saved_jobs:
                print(f"- Title: {job['title']}")
                print(f"  Description: {job['description']}")
                print(f"  Employer: {job['employer']}")
                print(f"  Location: {job['location']}")
                print(f"  Salary: {job['salary']}\n")

    def getJobCount(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Get the number of jobs in the database
                cursor.execute("SELECT COUNT(*) FROM jobs;")
                jobs_count = cursor.fetchone()[0]
        return jobs_count

    def writeJob(self, title, description, employer, location, salary, userID, first_name, last_name):
        now = datetime.datetime.now()
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Insert job details into the jobs table
                insert_query = """
                INSERT INTO jobs (title, description, employer, location, salary, user_id, first_name, last_name, date_posted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (title, description, employer,
                               location, salary, userID, first_name, last_name, now))

    def getJobsByUser(self, userID):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                    SELECT job_id, user_id, title, description, employer, location, salary 
                    FROM jobs 
                    WHERE user_id = %s;
                    """
                cursor.execute(fetch_query, (userID,))
                active_jobs = cursor.fetchall()
        return active_jobs

    def deleteJobFromDatabase(self, id):
        self.nullApplication(id)
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                delete_query = """
                        DELETE FROM jobs   
                        WHERE job_id = %s;
                        """
                cursor.execute(delete_query, (id,))

    def nullApplication(self, oldJob_id):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                update_query = """
                        UPDATE job_applications 
                        SET job_id = %s
                        WHERE job_id = %s;
                        """
                newJob_id = None
                cursor.execute(update_query, (newJob_id, oldJob_id))


    #############
    ## FRIENDS ##
    #############
    
    def sendConnectRequest(self, from_user_id, to_user_id):
        # Connect to the database
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Check if there's already a request or friendship between these two users
                check_query = """
                SELECT * FROM friendships 
                WHERE (student1_id = %s AND student2_id = %s) 
                OR (student1_id = %s AND student2_id = %s);
                """
                cursor.execute(check_query, (from_user_id,
                               to_user_id, to_user_id, from_user_id))
                existing_friendship = cursor.fetchone()

                if existing_friendship:
                    if existing_friendship[3] == 'pending':
                        print("There's already a pending request.")
                    else:
                        print("You're already connected with this user.")
                    return

                # Insert the connection request into the table
                insert_query = """
                INSERT INTO friendships (student1_id, student2_id, status) 
                VALUES (%s, %s, 'pending');
                """
                cursor.execute(insert_query, (from_user_id, to_user_id))
                connection.commit()

        print(f"Connection request sent to user {to_user_id}!")

    def checkPendingRequests(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT student1_id 
                FROM friendships 
                WHERE student2_id = %s AND status = 'pending';
                """
                cursor.execute(fetch_query, (self.userID,))
                requests = cursor.fetchall()

        if requests:
            print(f"\nYou have {len(requests)} pending friend requests!")
            for request in requests:
                # request[0] is student1_id, who sent the request
                self.handleFriendRequest(request[0])

    def handleFriendRequest(self, from_user_id):
        # Fetch the name of the person who sent the request for better UI
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                name_query = """
                SELECT first_name, last_name 
                FROM users 
                WHERE user_id = %s;
                """
                cursor.execute(name_query, (from_user_id,))
                name = cursor.fetchone()

        print(f"\nFriend request from: {name[0]} {name[1]}")

        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                while True:
                    choice = input(
                        "Do you want to accept this friend request? (yes/no): ").lower()
                    if choice == 'yes':
                        # Update the friendship status to confirmed
                        update_query = """
                        UPDATE friendships 
                        SET status = 'confirmed' 
                        WHERE student1_id = %s AND student2_id = %s;
                        """
                        cursor.execute(
                            update_query, (from_user_id, self.userID))
                        print("Friend request accepted!")
                        break
                    elif choice == 'no':
                        # Delete the friend request record
                        delete_query = """
                        DELETE FROM friendships 
                        WHERE student1_id = %s AND student2_id = %s;
                        """
                        cursor.execute(
                            delete_query, (from_user_id, self.userID))
                        print("Friend request rejected!")
                        break
                    else:
                        print("Unrecognized input. Please enter yes or no.")

    def viewPendingRequests(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT student1_id, first_name, last_name 
                FROM friendships JOIN users ON friendships.student1_id = users.user_id
                WHERE student2_id = %s AND status = 'pending';
                """
                cursor.execute(fetch_query, (self.userID,))
                requests = cursor.fetchall()

        if requests:
            print("\nPending Friend Requests:")
            for req in requests:
                print(f"User ID: {req[0]}, Name: {req[1]} {req[2]}")
        else:
            print("\nYou have no pending friend requests.")

    def getFriends(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Get friends where the current user is student1
                fetch_query_1 = """
                SELECT student2_id, first_name, last_name 
                FROM friendships JOIN users ON friendships.student2_id = users.user_id
                WHERE student1_id = %s AND status = 'confirmed';
                """
                cursor.execute(fetch_query_1, (self.userID,))
                friends_1 = cursor.fetchall()

                # Get friends where the current user is student2
                fetch_query_2 = """
                SELECT student1_id, first_name, last_name 
                FROM friendships JOIN users ON friendships.student1_id = users.user_id
                WHERE student2_id = %s AND status = 'confirmed';
                """
                cursor.execute(fetch_query_2, (self.userID,))
                friends_2 = cursor.fetchall()

        return friends_1 + friends_2

    def deleteConnection(self, friend_id):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Check if the given user_id exists in the friend's list
                check_query = """
                SELECT * FROM friendships 
                WHERE (student1_id = %s AND student2_id = %s) OR (student1_id = %s AND student2_id = %s);
                """
                cursor.execute(check_query, (self.userID,
                               friend_id, friend_id, self.userID))

                if cursor.fetchone():  # If exists
                    # Proceed to delete the friendship
                    delete_query = """
                    DELETE FROM friendships 
                    WHERE (student1_id = %s AND student2_id = %s) OR (student1_id = %s AND student2_id = %s);
                    """
                    cursor.execute(delete_query, (self.userID,
                                   friend_id, friend_id, self.userID))
                    return True
                else:
                    return False

    #############
    ## PROFILE ##
    #############

    def hasProfile(self, id):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"""SELECT *
                                    FROM profiles
                                    WHERE user_id = '{id}'""")
                    if not cursor.fetchall():
                        raise Exception
                    return True
                except:
                    return False

    def viewProfile(self, id):

        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"""SELECT (title, about)
                                    FROM profiles
                                    WHERE user_id = '{id}'""")
                    vals = list(cursor.fetchall()[0][0])
                    if not vals:
                        raise Exception
                except:
                    print("This user has not created a profile.")
                    return

                title, about = [vals[i] for i in range(2)]

                cursor.execute(f"""SELECT (first_name, last_name, university, major)
                                FROM users
                                WHERE user_id = '{id}'""")

                vals = list(cursor.fetchall()[0][0])
                first_name, last_name, university, major = [
                    vals[i] for i in range(4)]

                flag = 0
                try:
                    cursor.execute(f"""SELECT (school_name, degree, year_started, year_ended)
                                    FROM educations
                                    WHERE user_id = '{id}'""")
                    vals = list(cursor.fetchall()[0][0])
                    if not vals:
                        raise Exception
                except:
                    school_name = degree = year_started = year_ended = ""
                    flag = 1
                    has_education = 0
                if not flag:
                    has_education = 1
                    school_name, degree, year_started, year_ended = [
                        vals[i] for i in range(4)]

                flag = 0
                try:
                    cursor.execute(f"""SELECT (title, employer, date_started, date_ended, location, description)
                                    FROM experiences
                                    WHERE user_id = '{id}'""")
                    vals = list(cursor.fetchall())
                    if not vals:
                        raise Exception
                except:
                    has_experience = 0
                    flag = 1

                if not flag:
                    has_experience = 1

                    jobTitles = [None for i in range(len(vals))]
                    employers = [None for i in range(len(vals))]
                    dates_started = [None for i in range(len(vals))]
                    dates_ended = [None for i in range(len(vals))]
                    locations = [None for i in range(len(vals))]
                    descriptions = [None for i in range(len(vals))]

                    i = 0
                    for val in vals:
                        jobTitles[i], employers[i], dates_started[i], dates_ended[i], locations[i], descriptions[i] = [
                            val[0][j] for j in range(6)]
                        i += 1

        profile = f"""
                    {first_name} {last_name}
                    """
        if title:
            profile = profile + f"""
                    {title}
                    """

        if about:
            profile = profile + f"""
                    {about}
                    """

        profile = profile + f"""
                    University: {university}
                    Major: {major}
                    """

        if has_education:
            profile = profile + f"""
                    Attended {school_name} from {year_started} to {year_ended} to obtain a {degree}.
                    """

        if has_experience:
            for i in range(len(jobTitles)):
                profile = profile + f"""
                    Worked as a {jobTitles[i]} for {employers[i]}, from {dates_started[i]} to {dates_ended[i]}, at {locations[i]}:
                    {descriptions[i]}
                    """

        print(profile)

    def addEmptyJobExperience(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                connection._set_autocommit(True)
                cursor.execute(f"""
                            INSERT INTO experiences (user_id)
                            VALUES ('{self.userID}');
                            """)
                cursor.execute(f"""
                                SELECT experience_id
                                FROM experiences
                                WHERE user_id = '{self.userID}';
                                """)
                return cursor.fetchall()[-1][0]

    def addEmptyEducation(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                            INSERT INTO educations (user_id)
                            VALUES ('{self.userID}');
                            """)

    def addEmptyProfile(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                            INSERT INTO profiles (user_id)
                            VALUES ('{self.userID}');
                            """)
                
    def jobExperienceHelper(self):
        options = []
        jobs = []
        ids = []
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                flag = 0
                try:
                    cursor.execute(f"""SELECT *
                                    FROM experiences
                                    WHERE user_id = '{self.userID}'""")
                    vals = cursor.fetchall()
                    if not vals:
                        raise Exception
                except:
                    options.append("Add Job Experience")
                    flag = 1
                if not flag:
                    vals = list(vals)

                    print("Current job experience:")
                    for val in vals:
                        print(f"""
                            Worked as a {val[2]} for {val[3]} , from {val[4]} to {val[5]}, at {val[6]}.\n
                            {val[7]}
                            """)
                        jobs.append(f"{val[2]} for {val[3]}")
                        ids.append(val[0])
                    options.append("Edit Job Experience")
                    if len(vals) < 3:
                        options.append("Add Job Experience")

        options.append("Go Back")
        return options, jobs, ids

    def educationHelper(self):
        options = []
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                flag = 0
                try:
                    cursor.execute(f"""SELECT *
                                    FROM educations
                                    WHERE user_id = '{self.userID}'""")
                    vals = cursor.fetchall()
                    if not vals:
                        raise Exception
                except:
                    options.append("Add Education")
                    flag = 1
                if not flag:
                    vals = list(vals[0])
                    print(f"""
                          Current education:
                          Attended {vals[2]} from {vals[4]} to {vals[5]} to obtain a {vals[3]}.
                          """)
                    options.append("Edit Education")

        options.append("Go Back")
        return options

    ##############
    ## MESSAGES ##
    ##############

    def addMessageToDatabase(self, from_user_id, to_user_id, message):
        now = datetime.datetime.now()
        # Connect to the database
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Insert the message into the table
                insert_query = """
                INSERT INTO messages (sender, receiver, message_txt, status, sent_at) 
                VALUES (%s, %s, %s, 'unread', %s);
                """
                cursor.execute(
                    insert_query, (from_user_id, to_user_id, message, now))
                connection.commit()

        print(f"\nMessage sent to user {to_user_id}!")

    def getSenderID(self, message_id):
        # Retrieve the receiver ID of a message
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT sender 
                FROM messages 
                WHERE message_id = %s;
                """
                cursor.execute(fetch_query, (message_id,))
                receiver_id = cursor.fetchone()
                return receiver_id[0] if receiver_id else None

    def deleteMessage(self, message_id):
        # Mark the message as deleted
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                delete_query = """
                DELETE FROM messages 
                WHERE message_id = %s;
                """
                cursor.execute(delete_query, (message_id,))
        print("Message deleted.")

    def readMessage(self, message_id):
        # Read a specific message and update its status
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD,
                             host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT sender, message_txt
                FROM messages
                WHERE message_id = %s AND receiver = %s;
                """
                cursor.execute(fetch_query, (message_id, self.userID))
                message = cursor.fetchone()

        if message:
            sender_id, message_text = message
            sender_name = self.getUserName(sender_id)
            print(f"Message from: {sender_name}")
            print(f"Message: {message_text}")

            # Update the message status to 'read'
            with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD,
                                 host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    update_query = """
                    UPDATE messages
                    SET status = 'read'
                    WHERE message_id = %s;
                    """
                    cursor.execute(update_query, (message_id,))
                    connection.commit()
        else:
            print("Message not found in your inbox.")

    def getMessages(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Fetch all messages for the current user
                fetch_query = """
                SELECT message_id, sender, message_txt, status
                FROM messages 
                WHERE receiver = %s
                ORDER BY message_id;
                """
                cursor.execute(fetch_query, (self.userID,))
                messages = cursor.fetchall()
        return messages
    
    ###################
    ## NOTIFICATIONS ##
    ###################

    def notificationsMainMenu(self):
        InCollegeBackend.notiNotAppliedIn7Days(self)
        InCollegeBackend.notiNotCreatedProfile(self)
        InCollegeBackend.notiCheckMessages(self)
        InCollegeBackend.notiNewJobPosted(self)
        InCollegeBackend.notiJobDeleted(self)
        InCollegeBackend.notiNewStudents(self)

    def notificationsJob(self):
        InCollegeBackend.notiNumberOfJobsApplied(self)

    def notiNotAppliedIn7Days(self):
        try:
            with psycopg.connect(
                    dbname=self.DATABASE_NAME,
                    user=self.DATABASE_USER,
                    password=self.DATABASE_PASSWORD,
                    host=self.DATABASE_HOST,
                    port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    fetch_last_application_date_query = """
                    SELECT MAX(applied_at) 
                    FROM job_applications 
                    WHERE user_id = %s;
                    """
                    cursor.execute(fetch_last_application_date_query, (self.userID,))
                    last_application_date = cursor.fetchone()[0]

                    if last_application_date:
                        # Calculate the difference between the current date and the last application date
                        difference = datetime.datetime.now() - last_application_date

                        # If the difference is greater than 7 days, generate the notification
                        if difference.days >= 7:
                            print("\nRemember – you're going to want to have a job when you graduate. Make sure that you start to apply for jobs today!")
                    else:
                        # If the student hasn't applied for any jobs, generate the notification
                        print("\nRemember – you're going to want to have a job when you graduate. Make sure that you start to apply for jobs today!")

        except psycopg.Error as e:
            print(f"Error: {e}")

    def notiNotCreatedProfile(self):
        try:
            with psycopg.connect(
                    dbname=self.DATABASE_NAME,
                    user=self.DATABASE_USER,
                    password=self.DATABASE_PASSWORD,
                    host=self.DATABASE_HOST,
                    port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    check_query = """
                    SELECT user_id
                    FROM users
                    WHERE user_id = %s
                      AND user_id NOT IN (SELECT user_id FROM profiles);
                    """
                    cursor.execute(check_query, (self.userID,))
                    result = cursor.fetchone()

                    if result:
                        print("\nDon't forget to create a profile.")

        except psycopg.Error as e:
            print(f"Error: {e}")

    def notiCheckMessages(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT sender 
                FROM messages 
                WHERE receiver = %s AND status = 'unread';
                """
                cursor.execute(fetch_query, (self.userID,))
                messages = cursor.fetchall()

        if messages:
            print(f"\nYou have messages waiting for you in your inbox.\n")

    def notiNumberOfJobsApplied(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT COUNT(*) 
                FROM job_applications 
                WHERE user_id = %s;
                """
                cursor.execute(fetch_query, (self.userID,))
                number_of_jobs_applied = cursor.fetchone()[0]

        print(f"\nYou have currently applied for {number_of_jobs_applied} job(s).\n")

    def notiNewJobPosted(self):
        try:
            with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    fetch_query = """
                    SELECT user_id, title
                    FROM jobs
                    WHERE date_posted > (SELECT last_login FROM users WHERE user_id = %s) AND user_id != %s;
                    """
                    cursor.execute(fetch_query, (self.userID, self.userID))
                    new_jobs = cursor.fetchall()

                    for job in new_jobs:
                        user_id, title = job
                        print(f"\nA new job {title} has been posted by {user_id}.")

        except psycopg.Error as e:
            print(f"Error: {e}")
    
    def notiJobDeleted(self):
        try:
            with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    fetch_query = """
                    SELECT title
                    FROM job_applications
                    WHERE user_id = %s AND job_id IS NULL;
                    """
                    cursor.execute(fetch_query, (self.userID,))
                    jobs_deleted = cursor.fetchall()
                    
                    if jobs_deleted:
                        delete_query = """
                        DELETE FROM job_applications
                        WHERE user_id = %s AND job_id IS NULL;
                        """
                        cursor.execute(delete_query, (self.userID,))

                        for job in jobs_deleted:
                            print(f"\nA job that you applied for has been deleted: {job[0]}")

        except psycopg.Error as e:
            print(f"Error: {e}")

    def notiNewStudents(self):
        try:
            with psycopg.connect(
                    dbname=self.DATABASE_NAME,
                    user=self.DATABASE_USER,
                    password=self.DATABASE_PASSWORD,
                    host=self.DATABASE_HOST,
                    port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    fetch_query = """
                    SELECT user_id, first_name, last_name
                    FROM users
                    WHERE created_at > (SELECT last_login FROM users WHERE user_id = %s)
                      AND user_id != %s;
                    """
                    cursor.execute(fetch_query, (self.userID, self.userID))
                    new_students = cursor.fetchall()

                    for student in new_students:
                        user_id, first_name, last_name = student
                        print(f"\n{first_name} {last_name} has joined InCollege")

        except psycopg.Error as e:
            print(f"Error: {e}")

    ######################
    ## TIMESTAMP UPDATE ##
    ######################

    def update_last_login(self, user_id):
        now = datetime.datetime.now()
        try:
            with psycopg.connect(
                    dbname=self.DATABASE_NAME,
                    user=self.DATABASE_USER,
                    password=self.DATABASE_PASSWORD,
                    host=self.DATABASE_HOST,
                    port=self.DATABASE_PORT) as connection:
                with connection.cursor() as cursor:
                    update_query = """
                    UPDATE users
                    SET last_login = %s
                    WHERE user_id = %s;
                    """
                    cursor.execute(update_query, (now, user_id))
                    connection.commit()
        except psycopg.Error as e:
            print(f"Error updating last login: {e}")

