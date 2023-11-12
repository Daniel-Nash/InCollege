import re, helper, psycopg
from InquirerPy import prompt
from helper import InCollegeBackend
from psycopg.rows import dict_row

# Connect to your PostgreSQL server
DATABASE_NAME_ = "incollegedb"
DATABASE_USER_ = "postgres"
DATABASE_PASSWORD_ = "postgres"
DATABASE_HOST_ = "localhost" 
DATABASE_PORT_ = "5432"  # default PostgreSQL port

class InCollegeServer(InCollegeBackend):
    DATABASE_NAME = ""
    DATABASE_USER = ""
    DATABASE_PASSWORD = ""
    DATABASE_HOST = ""
    DATABASE_PORT = ""

    loggedIn = False
    userID = ""
    first_name = ""
    last_name = ""

    has_email = True
    has_sms = True
    has_ad = True
    language = "English"

    maxJobs = 10
    maxUsers = 10

    def messageMenu(self):
        while True:
            try:
                choice = prompt({"type": "list",
                                "message" : "Main Menu:",
                                "choices": ["Inbox", "Send Message", "Go Back"]})
                match choice[0]:
                    case "Inbox":
                        self.displayInbox()
                    case "Send Message":
                        self.sendMessageMenu()
                    case "Go Back":
                        return
                    case __:
                        raise ValueError
        
            except ValueError:              
                print("Invalid choice. Please enter a valid option.")

    def addJob(self):
        """
        Allows a logged-in user to post a job.
        """
        
        if self.getJobCount() >= self.maxJobs:
            print("You have reached the maximum number of job postings.")
            return

        print("\n============================\n")
        title = input("Please enter the job title: ")
        description = input("Please enter the job description: ")
        employer = input("Please enter the employer: ")
        location = input("Please enter the location: ")
        while True:
            try:
                salary_input = float(input('Please enter the salary: '))
                salary = round(salary_input, 2)  # Ensure it's rounded to 2 decimal places if needed
                break
            except ValueError:
                print("\nPlease enter a valid number for salary.\n")

        self.writeJob(title, description, employer, location, salary, self.userID, self.first_name, self.last_name)

        print("\nJob posted successfully!")
    
    def deleteJob(self):

        active_jobs = self.getJobsByUser(self.userID)

        options = []
        ids = []

        if active_jobs:
            print("\n List of Active Job Postings by The User \n")
            for jobs in active_jobs:
                options.append(f"Job ID: {jobs[0]}, User ID: {jobs[1]}, Title: {jobs[2]}, Description: {jobs[3]}, Employer: {jobs[4]}, Location: {jobs[5]}, Salary: {jobs[6]}")
                ids.append(jobs[0])
            options.append("Go Back")
            
            choice = prompt({
                    "type": "list",
                    "message" : "List of Jobs:",
                    "choices": options
                })
    
            if choice[0] == "Go Back":
                return
            
            else:
                id = options.index(choice[0])
                self.changeApplicationToZero(ids[id])
                self.deleteJobFromDatabase(ids[id])

        else:
            print("\nNo active job postings found.\n")
    
    def searchforAJob(self):
        # Connect to the database
        active_jobs = self.listJobs()

        options = []
        details = []
        
        if active_jobs: 
            print("\nActive Job Postings \n")

            for job in active_jobs:
                temp = f"Job ID: {job['job_id']}, Title: {job['title']}"
                if self.hasAppliedForJob(job['job_id']):
                    temp = temp + " (Applied to)"
                options.append(temp)
                details.append(f"Job ID: {job['job_id']} \nUser ID: {job['user_id']} \nTitle: {job['title']}, \nDescription: {job['description']}, \nEmployer: {job['employer']}, \nLocation: {job['location']}, \nSalary: {job['salary']}")
            options.append("Go Back")
            
            while True:
                choice = prompt({
                        "type": "list",
                        "message" : "List of Jobs:",
                        "choices": options
                    })
                
                if choice[0] == "Go Back":
                    return
                else:
                    id = options.index(choice[0])
                    print(details[id])
                    print('\n=================================\n')
                    
                    # After showing job details, offer options to save or apply
                    job_id = active_jobs[id]['job_id']
                    sub_choice = prompt({
                        "type": "list",
                        "message": "Job Options:",
                        "choices": ["Save/Unsave the Job", "Apply for the Job", "Go Back"]
                    })

                    if sub_choice[0] == "Save/Unsave the Job":
                        self.saveJobToDatabase(job_id)
                    elif sub_choice[0] == "Apply for the Job":
                        self.applyForJob(job_id)
                    elif sub_choice[0] == "Go Back":
                        continue

        else:
            print("\nNo active job postings found.\n")

    def signIn(self):
        """
        allow existing user to log in
        """
        while True:
            existingUserID = input("Please enter UserID: ")
            existingPassword = input("Please enter password: ")

            user = self.signInHelper(existingUserID, existingPassword)

            if user:
                self.userID = user['user_id']
                self.first_name = user['first_name']
                self.last_name = user['last_name']
                self.has_email = user['has_email']
                self.has_sms = user['has_sms']
                self.has_ad = user['has_ad']
                self.language = user['language']
                self.tier = user['tier']
                self.loggedIn = True
                

                print(f"\nWelcome, {self.userID}. You have successfully logged in.")
                return
            
            else:
                print("\nIncorrect username / password, please try again\n")

    def signUp(self):

        if self.getUserCount() >= self.maxUsers:
            print("\nAll permitted accounts have been created, please come back later\n")
            return

        """
        Registers a new user, provided the UserID is unique and the 
        password meets the requirements.
        """
        print("\n============================\n")

        while True:
            userID = input("Please enter UserID: ")
            if self.validUser(userID):
                break
            print("This username is already taken.")
        while True:
            print("===============================\n1) Password must be 8 - 12 characters\n2) Must contain at least one capital letter\n3) Must contain a number\n4) Must contain a special character\n =================================")
            password = input("Please enter password: ")
            if self.validPassword(password):
                break
            print("This password doesn't meet all the requirements.")
        first = input("Please enter your first name: ")
        last = input("Please enter your last name: ")
        university = input("Please enter your university: ").title()
        major = input("Please enter your major: ").title()
        try:
            choice = prompt({ "type": "list",
                                "message" : "Select a membership tier",
                                "choices": ["Standard (free)",
                                            "Plus ($10/month)"]
                })
            
            match choice[0]:
                case "Standard (free)":
                    tier = "Standard"

                case "Plus ($10/month)":
                    tier = "Plus"
                
                case __:  # <--- Else
                    raise ValueError
        
        except ValueError:
            print("Choice not found, please try again.\n") 
        
        has_email = True
        has_sms = True
        has_ad = True

        self.writeUser(userID, password, first, last, has_email, has_sms, has_ad, university, major, tier)

        print("\n============================\n")
        print("Thank you for creating an account.")

        self.userID = userID
        self.first = first
        self.last = last
        self.loggedIn = True
        self.has_email = True
        self.has_sms = True
        self.has_ad = True
        self.language = "English"
        self.tier = tier
        self.update_last_login(userID)
        
        print(f"\nWelcome, {self.userID}. You have successfully logged in.\n")
        
    def signInOrUp(self):
        """
        "Sign Up" Option under "General" under "Useful Link"
        This gives not logged-in user 3 choices to either sign in, sign up, or back
        """           
        run = True
        while run:
            try:
                # Ask for user input
                choice = prompt({
                    "type": "list",
                    "message": "General",
                    "choices": [
                        "Sign In",
                        "Sign Up",
                        "Back to General"
                    ]
                })

                match choice[0]:
                    case "Sign In":
                        self.signIn()
                        if self.loggedIn:
                            self.mainMenu()
                    case "Sign Up":
                        self.signUp()
                        if self.loggedIn:
                            self.mainMenu()

                    case "Back to General":
                        run = False
                        break
                        
                    case __:  # <--- Else
                        raise ValueError

            except ValueError:
                print("Choice not found, please try again.\n") 

    def searchExistingUsers(self):
        # Search Sign In by last name, university, or major
        # When results of these searches are displayed, the student will have the option of sending that student a
        # request to connect
        column_map = {
            "Last Name": "last_name",
            "University": "university",
            "Major": "major"
        }
        
        while True:
            try:
                choice_response = prompt({
                    "type": "list",
                    "message": "Search by:",
                    "choices": [
                        "Last Name",
                        "University",
                        "Major",
                        "Exit"
                    ]
                })

                choice = choice_response[0]

                if choice == "Exit":
                    return

                prompt_message = None
                if choice == "Last Name":
                    prompt_message = "Enter the user's last name: "
                elif choice == "University":
                    prompt_message = "Enter the university: "
                elif choice == "Major":
                    prompt_message = "Enter the major: "

                search_criteria = input(prompt_message)
                
                users = self.getUserByCriteria(column_map[choice], search_criteria)

                if users:
                    print("\nUser found in the InCollege system.\n")
                    # If logged in, show the option to connect
                    if self.loggedIn:
                        prompts = []
                        ids = []
                        for user in users:
                            ids.append(user[0])
                            prompts.append(f"User ID: {user[0]}, Name: {user[1]} {user[2]}, University: {user[3]}, Major: {user[4]}")
                        prompts.append("Go Back")
                        try:
                            choice_response = prompt({
                                "type": "list",
                                "message": "Users:",
                                "choices": prompts
                            })
                            if choice_response[0] == "Go Back":
                                break
                            elif choice_response[0] in prompts:
                                connect_choice = input("Do you want to send this user a request to connect? (yes/no): ").lower()
                                if connect_choice == "yes":
                                    # Handle sending a request
                                    self.sendConnectRequest(from_user_id = self.userID, to_user_id = ids[prompts.index(choice_response[0])])
                                else:
                                    print("Request not sent.")
                            else:
                                raise ValueError
                        except ValueError:
                            print("Invalid choice, please try again.\n")
                        
                    else:
                        for user in users:
                            print(f"User ID: {user[0]}, Name: {user[1]} {user[2]}, University: {user[3]}, Major: {user[4]}")
                        
                else:
                    print(f"\nNo user found with {choice}: {search_criteria}.\n")

            except ValueError:
                print("Invalid choice, please try again.\n")
                
    def changeLanguage(self):
        print("\nCurrent Language: " + self.language + "\n")

        while True:
            try:
                # Ask for user input
                choice = prompt({
                    "type": "list",
                    "message" : "Languages",
                    "choices": ["English",
                                "Spanish",
                                "Back to Important Links"]
                })

                match choice[0]:
                    case "English":
                        if self.language == "English":
                            print("\nCurrent Language is already in English\n")
                        else:
                            self.changeEntry("users", "language", "English")
                            print("\nLanguage changed to English\n")
                        
                    case "Spanish":
                        if self.language == "Spanish":
                            print("\nCurrent Language is already in Spanish\n")
                        else:
                            self.changeEntry("users", "language", "Spanish")
                            print("\nLanguage changed to Spanish\n")

                    case "Back to Important Links":
                        break

                    case __:  # <--- Else
                        raise ValueError

            except ValueError:
                print("Choice not found, please try again.\n")

    def guestControls(self):
        while True:
            if self.has_email == True:
                emailPreference = "ON"
            elif self.has_email == False:
                emailPreference = "OFF"

            if self.has_sms == True:
                smsPreference = "ON"
            elif self.has_sms == False:
                smsPreference = "OFF"
            
            if self.has_ad == True:
                adsPreference = "ON"
            elif self.has_ad == False:
                adsPreference = "OFF"
            
            print("\nCurrent preferences (Emails: " + emailPreference + ", SMS: " + smsPreference + ", Advertising: " + adsPreference + ")\n")
            
            try:
                # Ask for user input
                choice = prompt({ "type": "list",
                                    "message" : "Guest Controls",
                                    "choices": ["Email",
                                                "SMS",
                                                "Advertising",
                                                "Back to Important Links"]
                    })

                match choice[0]:
                    case "Email":
                        emailChoice = input("\nDo you want to receive InCollege emails? Type yes or no.\n").lower()

                        if emailChoice == "yes":
                            self.changeEntry("users", "has_email", True)
                            print("\nYou will keep receiving InCollege emails\n")
                        elif emailChoice == "no":
                            self.changeEntry("users", "has_email", False)
                            print("\nYou will stop receiving InCollege emails\n")
                        else: 
                            print("\nPlease type yes or no\n")

                    case "SMS":
                        SMSChoice = input("\nDo you want to receive InCollege SMS's? Type yes or no.\n").lower()

                        if SMSChoice == "yes":
                            self.changeEntry("users", "has_sms", True)
                            print("\nYou will keep receiving InCollege SMS's\n")
                        elif SMSChoice == "no":
                            self.changeEntry("users", "has_sms", False)
                            print("\nYou will stop receiving InCollege SMS's\n")
                        else: 
                            print("\nPlease type yes or no\n")

                    case "Advertising":
                        adsChoice = input("\nDo you want to receive InCollege advertising? Type yes or no.\n").lower()

                        if adsChoice == "yes":
                            self.changeEntry("users", "has_ad", True)
                            print("\nYou will keep receiving InCollege advertising\n")    
                        elif adsChoice == "no":
                            self.changeEntry("users", "has_ad", False)
                            print("\nYou will stop receiving InCollege advertising\n")
                        else: 
                            print("\nPlease type yes or no\n")

                    case "Back to Important Links":
                        break

                    case __:  # <--- Else
                        raise ValueError

            except ValueError:
                print("Choice not found, please try again.\n")

    def generalLinks(self):
        """
        "General" option under "Useful Links"
        """
        run = True
        while run:
            try:
                # Ask for user input
                choice = prompt({
                    "type": "list",
                    "message": "General",
                    "choices": [
                        "Sign Up",
                        "Help Center",
                        "About",
                        "Press",
                        "Blog",
                        "Careers",
                        "Developers",
                        "Back to Useful Links"
                    ]
                })

                match choice[0]:
                    case "Sign Up":
                        if self.loggedIn:
                            print("\nYou are already logged in!\n")
                        else:
                            self.signInOrUp()
                    case "Help Center":
                        print("\nWe're here to help.\n")
                    case "About":
                        print("\nIn College: Welcome to In College, the world's largest college student network with many users in many countries and territories worldwide.\n")
                    case "Press":
                        print("\nIn College Pressroom: Stay on top of the latest news, updates, and reports.\n")
                    case "Blog":
                        print("\nUnder construction.\n")
                    case "Careers":
                        print("\nUnder construction.\n")
                    case "Developers":
                        print("\nUnder construction.\n")
                    case "Back to Useful Links":
                        run = False
                        break
                    case __:  # <--- Else
                        raise ValueError
            except ValueError:
                print("Choice not found, please try again.\n")

    def usefulLinks(self):
        """
        Useful Links option
        """
        run = True
        while run:
            try:
                # Ask for user input
                choice = prompt({
                            "type": "list",
                            "message" : "Useful Links",
                            "choices": ["General", 
                                        "Browse InCollege", 
                                        "Business Solutions", 
                                        "Directories", 
                                        "Back to Main Menu"]
                })
                match choice[0]:
                    case "General":
                        self.generalLinks()
                    case "Browse InCollege":
                        print("\nUnder construction.\n")
                    case "Business Solutions":
                        print("\nUnder construction.\n")
                    case "Directories":
                        print("\nUnder construction.\n")
                    case "Back to Main Menu":
                        run = False
                        break
                    case __:    # <--- Else
                        raise ValueError
            except ValueError:
                print("Choice not found, please try again.\n")

    def importantLinks(self):
        """
        Important Links option
        """
        while True:
            try:
                # Ask for user input
                choice = prompt({
                            "type": "list",
                            "message" : "Important Links",
                            "choices": ["A Copyright Notice",
                                        "About",
                                        "Accessibility", 
                                        "User Agreement", 
                                        "Privacy Policy", 
                                        "Cookie Policy", 
                                        "Copyright Policy", 
                                        "Brand Policy", 
                                        "Guest Controls", 
                                        "Languages",
                                        "Back to Main Menu"]
                })
                match choice[0]:
                    case "A Copyright Notice":
                        print("\n© 2023 InCollege\n")

                    case "About":
                        print("\nWe're InCollege, a social networking solution made by college students for college students.\n")

                    case "Accessibility":
                        print("\nInCollege is designed with navigation, readability, and usability, which benefits all users. By adding alt text to images and ensuring a logical content structure we have achieved to be ADA compliant and all users including those with disabilities can enjoy our services.\n")

                    case "User Agreement":
                        print("\nDisclaimer: By using InCollege you agree to everything our policies say, including data being collected from you, the use of cookies on your computer, and copyright law applicable to you, among others. Please check our Privacy, Cookie, Copyright, and Brand policies for more detailed information.\n")

                    case "Privacy Policy":
                        print("\nThis Website collects some Personal Data from its Users. Among the types of Personal Data that this Website collects, by itself or through third parties, there are: email address; password; first name; last name; among various types of Data. The Owner takes appropriate security measures to prevent unauthorized access, disclosure, modification, or unauthorized destruction of the Data.\n")
                        if self.loggedIn == False:
                            print("\nYou need to be logged in to access guest controls.\n")
                        else:
                            self.guestControls()

                    case "Cookie Policy":
                        print("\nCookies are small data files that are placed on your computer or mobile device when you visit a website. Cookies are widely used by website owners in order to make their websites work, or to work more efficiently, as well as to provide reporting information. Cookies help us deliver our services, by using our services, you agree to our use of cookies in your computer.\n")

                    case "Copyright Policy":
                        print("\nExcept as permitted by the copyright law applicable to you, you may not reproduce or communicate any of the content on this website, including files downloadable from this website, without the permission of the copyright owner.\n")

                    case "Brand Policy":
                        print("\nInCollege understands how hard it is for students looking for a first job and will provide the tools that they need in order to be successful. Our goal is to continuously advance what's possibly in education and connect students from all around the world.\n")

                    case "Guest Controls":
                        if self.loggedIn == False:
                            print("\nYou need to be logged in to access guest controls.\n")
                        else:
                            self.guestControls()

                    case "Languages":
                        if self.loggedIn == False:
                            print("\nYou need to be logged in to change the language.\n")
                        else:
                            self.changeLanguage()

                    case "Back to Main Menu":
                        break

                    case __:  # <--- Else
                        raise ValueError

            except ValueError:
                    print("Choice not found, please try again.\n")

    def editJobExperience(self, id):
        while True:
            choice = prompt({
                    "type": "list",
                    "message": "Edit Job Experience",
                    "choices": ["Title", "Employer", "Date Started", "Date Ended", "Location", "Description", "Finish"]
                })

            if choice[0] == "Finish":
                if self.completeRow('experiences', ['experience_id', id]):
                    break
                else:
                    print("You have missing information. Complete each field before finishing.")
            
            else:
                if choice[0] == "Date Started" or choice[0] == "Date Ended":
                    entry = helper.getDate()
                else:
                    entry = input(f"Change {choice[0]} to what? ")
                # add logic to verify/change input based on selection
                column = choice[0].lower().replace(' ', '_')
                self.changeEntry("experiences", column, entry, "experience_id", id)

    def jobExperience(self):
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

        try: 
            choice = prompt({
                "type": "list",
                "message" : "Job Experience:",
                "choices": options
            })

            match choice[0]:

                case "Go Back":
                    return
                case "Edit Job Experience":
                    if len(jobs) == 1:
                        id = ids[0]
                    else:
                        choice = prompt({
                            "type": "list",
                            "message" : "Edit Job Experience:",
                            "choices": jobs
                        })
                        id = ids[jobs.index(choice[0])]
                    self.editJobExperience(id)
                case "Add Job Experience":
                    id = self.addEmptyJobExperience()
                    self.editJobExperience(id)
                case __:
                    raise ValueError
            
        except ValueError:              
            print("Invalid choice. Please enter a valid option.")

    def applyForJob(self, job_id):
        # Check if the user has already applied for this job
        if self.hasAppliedForJob(job_id):
            print("You have already applied for this job. You cannot apply again.")
            return
        # Check if the user has posted this job
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM jobs WHERE job_id = %s", (job_id,))
                job_user_id = cursor.fetchone()
                if job_user_id and job_user_id[0] == self.userID:
                    print("You cannot apply for a job you have posted.")
                    return
        # Fetch title of the job
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT title FROM jobs WHERE job_id = %s", (job_id,))
                job_title = cursor.fetchone()
        print("Graduation Date Information:")
        graduation_date = helper.getDate()
        print("Start Date Information:")
        start_date = helper.getDate()
        paragraph_text = input("Explain why you think you would be a good fit for this job: ")

        # Store the application in the database
        self.storeJobApplication(job_id, job_title[0], graduation_date, start_date, paragraph_text)

        print("Application submitted successfully!")

    def editEducation(self):
        while True:
            choice = prompt({
                    "type": "list",
                    "message": "Edit Education",
                    "choices": ["School Name", "Degree", "Year Started", "Year Ended", "Finish"]
                })
            
            if choice[0] == "Finish":
                if self.completeRow('educations'):
                    break
                else:
                    print("You have missing information. Complete each field before finishing.")

            else:
                while True:
                    entry = input(f"Change {choice[0].lower()} to what? ")
                    if choice[0] == "Year Started" or choice[0] == "Year Ended":
                        if entry.isnumeric():
                            if int(entry) > 1 and int(entry) < 9999:
                                break
                        print("Please input a valid year.")
                        continue
                    break

                # add logic to verify/change input based on selection
                column = choice[0].lower().replace(' ', '_')
                self.changeEntry("educations", column, entry)

    def education(self):

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

        try: 
            choice = prompt({
                "type": "list",
                "message" : "Education:",
                "choices": options
            })

            match choice[0]:

                case "Go Back":
                    return
                case "Edit Education":
                    self.editEducation()
                case "Add Education":
                    self.addEmptyEducation()
                    self.editEducation()
                case __:
                    raise ValueError
            
        except ValueError:              
            print("Invalid choice. Please enter a valid option.")

    def editProfile(self):
        while True:
            choice = prompt({
                    "type": "list",
                    "message": "Edit Profile",
                    "choices": ["First Name", "Last Name", "Title", "Major", "University", "About", "Education", "Job Experience", "Finish"]
                })
            
            if choice[0] == "Finish":
                break
            elif choice[0] == "Education":
                self.education()
            elif choice[0] == "Job Experience":
                self.jobExperience()
            else:
                entry = input(f"Change {choice[0]} to what? ")
                
                if choice[0] == "Major" or choice[0] == "University":
                    entry = entry.title()
                # add logic to verify/change input based on selection
                column = choice[0].lower().replace(' ', '_')
                table_map = {
                    "first_name": "users",
                    "last_name": "users",
                    "title": "profiles",
                    "major": "users",
                    "university": "users",
                    "about" : "profiles"
                }
                self.changeEntry(table_map.get(column), column, entry)

    def profile(self):
        options = []
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                flag = 0
                try:
                    cursor.execute(f"""SELECT (title, about)
                                    FROM profiles
                                    WHERE user_id = '{self.userID}'""")
                    vals = cursor.fetchall()
                    if not vals:
                        raise Exception
                except:
                    options.append("Create Profile")
                    flag = 1
                if not flag:
                    options.append("Edit Profile")
                    self.viewProfile(self.userID)

        options.append("Go Back")
        
        try: 
            choice = prompt({
                "type": "list",
                "message" : "Profile:",
                "choices": options
            })

            match choice[0]:
                
                case "Go Back":
                    return
                case "Edit Profile":
                    self.editProfile()
                    print("Profile Edited")
                case "Create Profile":
                    self.addEmptyProfile()
                    self.editProfile()
                    print("Profile Created")
                case __:
                    raise ValueError

        except ValueError:              
            print("Invalid choice. Please enter a valid option.")

    def mainMenu(self):
        """
        Displays the main menu to the user after they log in.
        """
        # loggedIn = True
        while True:
            membershipTier = str(self.tier)
            print("\nMembership: " + membershipTier)
            #Display current language
            print("Current Language: " + self.language)
            #Display preferences
            if self.has_email == True:
                emailPreference = "ON"
            elif self.has_email == False:
                emailPreference = "OFF"
            
            if self.has_sms == True:
                smsPreference = "ON"
            elif self.has_sms == False:
                smsPreference = "OFF"
            
            if self.has_ad == True:
                adsPreference = "ON"
            elif self.has_ad == False:
                adsPreference = "OFF"
            
            print("Current preferences (Emails: " + emailPreference + ", SMS: " + smsPreference + ", Advertising: " + adsPreference + ")")
            self.checkPendingRequests()
            self.notificationsMainMenu()
            self.update_last_login(self.userID)

            try: 
                choice = prompt({
                                "type": "list",
                                "message" : "Main Menu:",
                                "choices": ["Find someone you know", 
                                            "Job search/internship", 
                                            "Learn a new skill",
                                            "Useful Links", 
                                            "InCollege Important Links",
                                            "Profile",
                                            "View Pending Connection Requests",
                                            "Show my Network",
                                            "Disconnect from a Connection",
                                            "Messages",
                                            "Log out"]
                })
                
                match choice[0]:
                    case "Find someone you know":
                    # Call the searchExistingUsers function
                        self.searchExistingUsers()
                
                    case "Job search/internship":
                        while True:
                            self.notificationsJob()
                            try:
                                choice = prompt({
                                        "type": "list", 
                                        "message" : "Select one:",
                                        "choices": ["Search for a Job", "Post a Job", "Delete a Job" , "List of Applied Jobs", "List not Applied Jobs" , "List of Saved Jobs", "Back to the main menu"]
                                })

                                match choice[0]:
                                    case "Search for a Job":
                                        self.searchforAJob()
                                    case "Post a Job":
                                        self.addJob()
                                    case "Delete a Job":
                                        self.deleteJob()
                                    case "List of Applied Jobs":
                                        self.listAppliedJobs()
                                    case "List not Applied Jobs":
                                        self.listUnappliedJobs()
                                    case "List of Saved Jobs":
                                        self.listSavedJobs()
                                    case "Back to the main menu":
                                        break  
                                    case __:    # <--- Else
                                        raise ValueError
                            
                            except ValueError:              
                                print("Invalid choice. Please enter a valid option.")

                
                    case "Learn a new skill":
                        while True:
                            try:
                                choice = prompt({
                                        "type": "list",
                                        "message" : "Skills Available:",
                                        "choices": ["Team Work", "Clean Code", "Customer Service", "Marketing", "Management", "Back to the main menu"]
                                })
                                
                                match choice[0]:
                                    case "Team Work":
                                        print("\nunder construction.\n")
                                    case "Clean Code":
                                        print("\nunder construction.\n")
                                    case "Customer Service":
                                        print("\nunder construction.\n")
                                    case "Marketing":
                                        print("\nunder construction.\n")
                                    case "Management":
                                        print("\nunder construction.\n")
                                    case "Back to the main menu":
                                        break
                                    case __:    # <--- Else
                                        raise ValueError
                        
                            except ValueError:              
                                print("Invalid choice. Please enter a valid option.")
                        
                    case "Useful Links":
                        self.usefulLinks()
                    case "InCollege Important Links":
                        self.importantLinks() 
                    case "Profile":
                        self.profile()
                    case "View Pending Connection Requests":
                        self.viewPendingRequests()
                    case "Show my Network":
                        self.viewConnectedFriends()
                    case "Disconnect from a Connection":
                        self.disconnectFriend()
                    case "Messages":
                        self.messageMenu()
                    case "Log out":
                        # Restore the variables
                        self.userID = ""
                        self.loggedIn = False
                        self.first_name = ""
                        self.last_name = ""
                        self.has_email = True
                        self.has_sms = True
                        self.has_ad = True
                        self.language = "English"

                        print("\nLogging out.\n")
                        break
                    case __:    # <--- Else
                        raise ValueError
            
            except ValueError:
                print("\nInvalid choice. Please enter a valid option.\n")

    def loginScreen(self):
        print("\n Welcome to InCollege!")
        print("\n======================================\n")
        print("Steven's story:\n")
        print("When I first started college during my freshman year I was very shy and didn’t really have many close friends or connections to other people besides my small circle of friends. On top of that, I was looking for a part-time job to help my parents pay my tuition for college, the problem was that I didn’t really had a resume to boast about or any real work history and no working professional really wanted to talk to me. That same freshman year a professor introduced us to InCollege during a class and I tried it out of curiosity, it made all the difference! InCollege allowed me to connect with other college students at other universities who were in my major and talk about school, jobs, and projects. Being online meant that even if I was shy I was still able to create relationships with real people and expand my connections. Having connections made all the difference when talking to people about job, salaries, and offers. InCollege understands that everyone's looking for a first job and will provide the tools that they need in order to be successful. Not only was I able to find a part-time job during my college years, but it even landed me a job I was not expecting. One of my friends I made during inCollege got the job first and after working there for a while referred me to his boss, I already had a position at a well-recognized company before I even graduated! By the time I transitioned to LinkedIn I had more experiences I could use on my resume. My time using InCollege really made all the difference for me and sure it will help you too. Whether it is creating an identity on inCollege, creating connections with other students from other universities, or accessing job information, inCollege will help provide you the tools you need.")
        print("\n======================================\n")
        while True:
            try:
                # Ask for user input
                choice = prompt({
                            "type": "list",
                            "message" : "Login page",
                            "choices": ["Learn why you should join InCollege", 
                                        "Sign In", 
                                        "Sign Up", 
                                        "Find an Existing User",
                                        "Useful Links",
                                        "InCollege Important Links",
                                        "Exit"]
                })
                match choice[0]:
                    case "Sign In":
                        self.signIn()
                        if self.loggedIn:
                            self.mainMenu()
                    case "Sign Up":
                        self.signUp()
                        if self.loggedIn:
                            self.mainMenu()
                    case "Find an Existing User":
                    # Call the searchExistingUsers function
                        self.searchExistingUsers()
                    case "Learn why you should join InCollege":
                        print("\n============================\n============================\n====Video is now playing====\n============================\n============================\n")
                    case "Useful Links":
                        self.usefulLinks()
                    case "InCollege Important Links":
                        self.importantLinks()
                    case "Exit":
                        print("Thank you, bye!\n")
                        break
                    case __:    # <--- Else
                        raise ValueError
            
            except ValueError:
                    print("Choice not found, please try again.\n")
    
    def viewConnectedFriends(self):
        
        friends = self.getFriends()
        options = []
        ids = []
        if friends:
            print("\nList of Friends:")
            for friend in friends:
                options.append(f"User ID: {friend[0]}, Name: {friend[1]} {friend[2]}")
                if self.hasProfile(friend[0]):
                    options[-1] = options[-1] + " (View Profile)"
                ids.append(friend[0])
            options.append("Go Back")

            choice = prompt({
                            "type": "list",
                            "message" : "View My Network:",
                            "choices": options
                        })
            
            if choice[0] == "Go Back":
                return

            while True:
                try:
                    sub_choice = prompt({
                                "type": "list",
                                "message" : "What do you want to do?:",
                                "choices": ["View Profile", 
                                            "Send Message", 
                                            "Go Back"]
                    })
                    match sub_choice[0]:
                        case "View Profile":
                            self.viewProfile(ids[options.index(choice[0])])
                        
                        case "Send Message":
                            self.addMessageToDatabase(from_user_id = self.userID, to_user_id = ids[options.index(choice[0])])

                        case "Go Back":
                            return

                        case __:    # <--- Else
                            raise ValueError
            
                except ValueError:
                        print("Choice not found, please try again.\n")

        else:
            print("\nYou have no connections in the system.")

    def disconnectFriend(self):
        friend_id = input("Enter the User ID of the connection you want to disconnect from: ")
        if self.deleteConnection(friend_id):
            print("Successfully disconnected!")
        else:
            print("The given user is not in your connection list.")
    
    def sendMessageMenu(self):
        if self.tier == "Standard":
            #Standard members can only send messages from people who have accepted their friend requests
            self.sendMessageToFriend()
        elif self.tier == "Plus":
            #Plus members can generate a list of all the students who are in the system and can send a message to any of them
            while True:
                try:
                    choice = prompt({
                                "type": "list",
                                "message" : "Send message to:",
                                "choices": ["A friend", 
                                            "Show all students", 
                                            "Go Back"]
                    })
                    match choice[0]:
                        case "A friend":
                            self.sendMessageToFriend()
                        
                        case "Show all students":
                            self.sendMessageToUser()

                        case "Go Back":
                            return

                        case __:    # <--- Else
                            raise ValueError
            
                except ValueError:
                        print("Choice not found, please try again.\n")
    
    def sendMessageToFriend(self):
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

        friends = friends_1 + friends_2
        options = []
        ids = []
        if friends:
            print("\nSend message to:")
            for friend in friends:
                options.append(f"User ID: {friend[0]}, Name: {friend[1]} {friend[2]}")
                ids.append(friend[0])
            options.append("Go Back")

            choice = prompt({
                            "type": "list",
                            "message" : "List of Friends:",
                            "choices": options
                        })
                
            if choice[0] == "Go Back":
                return

            self.addMessageToDatabase(from_user_id = self.userID, to_user_id = ids[options.index(choice[0])])

        else:
            print("\nYou have no connections in the system.")

    def sendMessageToUser(self):
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                # Construct the query
                fetch_query = f"""
                SELECT user_id, first_name, last_name 
                FROM users; 
                """
                cursor.execute(fetch_query)
                users = cursor.fetchall()
            
        options = []
        ids = []       
        if users:
            print("\nSend message to:")
            for user in users:
                options.append(f"User ID: {user[0]}, Name: {user[1]} {user[2]}")
                ids.append(user[0])
            options.append("Go Back")

            choice = prompt({
                    "type": "list",
                    "message" : "List of Users:",
                    "choices": options
                })
                
            if choice[0] == "Go Back":
                return

            self.addMessageToDatabase(from_user_id = self.userID, to_user_id = ids[options.index(choice[0])])

        else:
            print("\nYou have no connections in the system.")
 
    def displayInbox(self):
        
        while True:

            options = []
            ids = []

            messages = self.getMessages()

            if not messages:
                print("\nNo messages in your inbox.")
                options.append("Go Back")

            else:

                for message in messages:
                    message_id, sender_id, message_txt, status = message
                    sender_name = self.getUserName(sender_id)
                    option = ""
                    if status == 'unread':
                        option += "(UNREAD) "
                    option += f"{sender_name}: {message_txt[:19]}"
                    if len(message_txt) > 20:
                        option += "..."
                    options.append(option)
                    ids.append(message_id)

                options.append("Go Back")


            choice = prompt({
                                    "type": "list",
                                    "message" : "Messages:",
                                    "choices": options
                            })
            
            if choice[0] == "Go Back":
                return
            
            id = ids[options.index(choice[0])]
            self.readMessage(id)

            while True:
                sub_choice = prompt({
                                    "type": "list",
                                    "message" : "Skills Available:",
                                    "choices": ["Respond to Message", "Delete Message", "Go Back"]
                                    })
                
                match sub_choice[0]:
                    case "Go Back":
                        break
                    case "Respond to Message":
                        receiver_id = self.getSenderID(id)
                        self.respondToMessage(receiver_id)
                    case "Delete Message":
                        self.deleteMessage(id)
                        options.pop(options.index(choice[0]))
                        break

    def respondToMessage(self, receiver_id):
        message = input("Enter your response: ")
        
        # Insert the response message into the table
        with psycopg.connect(dbname=self.DATABASE_NAME, user=self.DATABASE_USER, password=self.DATABASE_PASSWORD, host=self.DATABASE_HOST, port=self.DATABASE_PORT) as connection:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO messages (sender, receiver, message_txt, status) 
                VALUES (%s, %s, %s, 'unread');
                """
                cursor.execute(insert_query, (self.userID, receiver_id, message))
        print("Response message sent.")

    def __init__(self, databaseName = DATABASE_NAME_, databaseUser = DATABASE_USER_, databasePassword = DATABASE_PASSWORD_, databaseHost = DATABASE_HOST_, databasePort = DATABASE_PORT_):
        self.DATABASE_NAME = databaseName
        self.DATABASE_USER = databaseUser
        self.DATABASE_PASSWORD = databasePassword
        self.DATABASE_HOST = databaseHost
        self.DATABASE_PORT = databasePort
        self.loginScreen()

def main():
    try:
        psycopg.connect(dbname=DATABASE_NAME_, user=DATABASE_USER_, password=DATABASE_PASSWORD_, host=DATABASE_HOST_, port=DATABASE_PORT_)
    except:
        print(f"Could not connect to database {DATABASE_NAME_}. Creating it locally...")
        helper.createDatabase(DATABASE_USER_, DATABASE_PASSWORD_, DATABASE_NAME_, DATABASE_HOST_, DATABASE_PORT_)
    
    InCollegeServer()

if __name__ == "__main__":
    main()


