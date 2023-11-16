import main, pytest, psycopg, helper, datetime
from main import DATABASE_NAME_, InCollegeServer

sourceFilename = 'main'
promptModule = sourceFilename + '.prompt'

# List of tables and their sequences if any.
# Dependent tables (with foreign keys) should be deleted before primary tables.
tables_sequences = {
    "messages": "messages_message_id_seq",
    "job_applications": None,
    "saved_jobs": None,
    "educations": None,
    "experiences": None,
    "profiles": None,
    "jobs": "jobs_job_id_seq",
    "friendships": None,
    "users": None
}

defaultUser = "pyTestUser"
defaultPassword = "pyTest123%"
defaultFirstName = "pyTest"
defaultLastName = "User"
defaultEmailPref = True
defaultSMSPref = True
defaultAdsPref = True
defaultLanguage = "English"
defaultUniversity = "University of South Florida".title()
defaultMajor = "Computer Science".title()
defaultTier = "Standard"
defaultFakeTime = datetime.datetime.now()
defaultCreationTime = defaultFakeTime
defaultLastLogin = defaultFakeTime
defaultUserTuple = (defaultUser, hash(defaultPassword), defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor, defaultTier, defaultCreationTime, defaultLastLogin)
defaultUserTable = [[defaultUserTuple]]
maxUsers = 10

defaultTitle = "pyTester"
defaultDescription = "testsPython"
defaultEmployer = "pyTest"
defaultLocation = "pyTest"
defaultSalary = "0"
defaultDatePosted = defaultFakeTime
defaultJobTuple = (1, defaultUser, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary, defaultFirstName, defaultLastName, defaultDatePosted)
defaultJobTable = [[defaultJobTuple]]
maxJobs = 10

defaultProfileTitle = "Title"
defaultProfileAbout = "About"

defaultGraduationYear = 2030
defaultGraduationMonth = 3
defaultGraduationDay = 30
defaultGraduationDate = f"{defaultGraduationYear}-{defaultGraduationMonth}-{defaultGraduationDay}"
defaultGraduationDatetime = datetime.date(defaultGraduationYear, defaultGraduationMonth, defaultGraduationDay)
defaultStartYear = 2031
defaultStartMonth = 1
defaultStartDay = 1
defaultStartDate = f"{defaultStartYear}-{defaultStartMonth}-{defaultStartDay}"
defaultStartDatetime = datetime.date(defaultStartYear, defaultStartMonth, defaultStartDay)
defaultApplicationDescription = "compellingExplanation"
defaultApplicationTuple = (1, defaultUser, 1, defaultTitle, defaultGraduationDatetime, defaultStartDatetime, defaultApplicationDescription, defaultFakeTime)

defaultMessage = "pyTestMessage"
defaultConcatenatedMessage = defaultMessage[:19]
if len(defaultMessage) > 20: defaultConcatenatedMessage += "..."

DATABASE_TEST_NAME = "incollegetestdb"
DATABASE_ORIGINAL = DATABASE_NAME_

DATABASE_NAME = DATABASE_TEST_NAME
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"
DATABASE_HOST = "localhost" 
DATABASE_PORT = "5432"

@pytest.fixture
def freezeTime(monkeypatch):
    class freeze(datetime.datetime):
        @classmethod
        def now(cls):
            return defaultFakeTime

    monkeypatch.setattr(datetime, 'datetime', freeze)

def dropTestDatabase():
    try:
      with psycopg.connect(dbname=DATABASE_ORIGINAL, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
        connection._set_autocommit(True)
        with connection.cursor() as cursor:
            cursor.execute(f"""DROP DATABASE {DATABASE_TEST_NAME};""")
    except:
      pass

def clear():
    with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
        with connection.cursor() as cursor:
            for table, sequence in tables_sequences.items():
                # Try deleting data from the table
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except Exception as e:
                    print(f"Error deleting data from {table}: {e}")
                    exit()

                # If there's a sequence associated, reset it
                if sequence:
                    try:
                        cursor.execute(f"ALTER SEQUENCE {sequence} RESTART WITH 1")
                    except Exception as e:
                        print(f"Error resetting sequence {sequence}: {e}")
                        exit()

            # Commit all changes to the database
            connection.commit()

# function to start tests which require an existing user to be able to log in
# don't use this function unless you need an existing user! start the function with clear() instead
def addTestUser(num = 1):
  clear()
  finalTuple = [[defaultUserTuple]]
  rows = [list(defaultUserTuple)]

  if num > 1:
      
      for i in range(1, num):
        userTuple = list(defaultUserTuple)
        userTuple[0] = f"{defaultUser}{str(i)}"
        rows.append(userTuple)
        finalTuple[0].append(tuple(userTuple))

  addRowsToTable(rows, 'users')
  return finalTuple
  
def readDB(select = "all"):
    read = []
    with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
        with connection.cursor() as cursor:
            if select != "all":
              try:
                  cursor.execute(f"""SELECT *
                                  FROM {select}""")
                  read.append(cursor.fetchall())
              except Exception as e:
                  print(f"Error executing query: {e}")
            else:
              for table in tables_sequences:
                  try:
                      cursor.execute(f"""SELECT *
                                      FROM {table}""")
                      read.append(cursor.fetchall())
                  except Exception as e:
                      print(f"Error executing query: {e}")
    return read

def addRowsToTable(rows, table):
  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    connection._set_autocommit(True)
    with connection.cursor() as cursor:
      try:
        with cursor.copy(f"COPY {table} FROM STDIN") as copy:
          for row in rows:
            copy.write_row(row)
        if tables_sequences[table]:
          cursor.execute(f"""ALTER SEQUENCE {tables_sequences[table]} RESTART WITH {readDB(table)[0][-1][0] + 1}""")
      except Exception as e:
          print(f"Error executing query: {e}")
          exit()

dropTestDatabase()
helper.createDatabase(DATABASE_USER, DATABASE_PASSWORD, DATABASE_TEST_NAME, DATABASE_HOST, DATABASE_PORT)

###########
## TESTS ##
###########

# note that many of the inputs for these tests will look similar
# this is because we have to get the program to terminate to test the output stream; this is only possible by logging out in most cases

# pyTest basics:
# the file name MUST be "{filename}_test.py"
# each function to be executed by pyTest MUST begin with "test"
# pyTest will execute each such function itself; they do not need to (and should not) be called
# every pyTest function is basically a compound AND statement that each assert statement is true (which means that a pyTest with no assert statements will always pass!)

# 'monkeypatch' and 'capsys' are python fixtures; to use them they need to be included as function parameters
# monkeypatch is used to override functions - we can tell python to skip a function's normal behavior and return what we tell it to instead
# this is used for keyboard input (the input() builtin) and for prompt selection (InquirerPy's prompt() )
# capsys is used to capture the stdout stream
# capsys.readouterr() captures (and consumes) the current stdout and stderr streams
# we only care about the stdout stream (the print statements we want to look at), which we get with the .out object (which gives us a string)
# the .split('\n') string method changes the string into a list of strings separated by the newline character ("This is an example".split(' ') returns ['This', 'is', 'an', 'example'])
# finally, we use array subscripting to get the output string we're looking for. In most cases I've used the second-to-last string (the last string is empty), which should be "Logging out." for most test cases
# but we can target any string, so for example we can assert that the nth string will be "All permitted accounts have been created..." for a test case that tests the 5 user limit functionality

# tests if the main screen exits correctly
def test_mainScreen(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  captured_output = capsys.readouterr().out
  assert captured_output.split('\n')[-3] == "Thank you, bye!"

# tests if the main screen prints the success story
def test_mainScreenStory(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  captured_output = capsys.readouterr().out
  assert "When I first started college" in captured_output

# tests if the 'learn why you should join inCollege' option prints correctly
def test_mainScreenVideo(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Learn why you should join InCollege'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  captured_output = capsys.readouterr().out
  assert "Video is now playing" in captured_output

# tests main screen existing user search
def test_mainScreenSearchUserByLastName(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Find an Existing User'}, {0: 'Last Name'}, {0: 'Exit'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultLastName])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"User found in the InCollege system.\n\nUser ID: {defaultUser}, Name: {defaultFirstName} {defaultLastName}, University: {defaultUniversity}, Major: {defaultMajor}"\
          in capsys.readouterr().out

def test_mainScreenSearchUserByUniversity(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Find an Existing User'}, {0: 'University'}, {0: 'Exit'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUniversity])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"User found in the InCollege system.\n\nUser ID: {defaultUser}, Name: {defaultFirstName} {defaultLastName}, University: {defaultUniversity}, Major: {defaultMajor}"\
          in capsys.readouterr().out

def test_mainScreenSearchUserByMajor(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Find an Existing User'}, {0: 'Major'}, {0: 'Exit'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultMajor])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"User found in the InCollege system.\n\nUser ID: {defaultUser}, Name: {defaultFirstName} {defaultLastName}, University: {defaultUniversity}, Major: {defaultMajor}"\
          in capsys.readouterr().out

# tests main screen existing user search with name that is not registered with inCollege
def test_mainScreenSearchInvalidUser(monkeypatch, capsys):
  addTestUser()

  testNames = ["pyTest", "py", "Test", ""]

  for testName in testNames:

    prompts = iter([{0: 'Find an Existing User'}, {0: 'Last Name'}, {0: 'Exit'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testName])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert f"No user found with Last Name: {testName}." in capsys.readouterr().out

# tests new user creation with valid username/password
def test_newUser(monkeypatch, capsys, freezeTime):
  clear()

  testUsernamesPasswords = [["pyTestUser", "pyTest123%"],
                            ["pyTestUser2", "PYTEST123!"],
                            ["thisIsALongTestStringPyTestUser3", "1aBcd&&&&"],
                            ["4", "999ZZZZ^"], ["b", "kOp0`-2fwe"]]

  users = [[]]

  for testUsernamePassword in testUsernamesPasswords:

    prompts = iter([{0: 'Sign Up'}, {0: 'Standard (free)'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    
    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
    users[0].append((testUsernamePassword[0], hash(testUsernamePassword[1]), defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor, defaultTier, defaultCreationTime, defaultLastLogin))
    assert readDB("users") == users

# tests new user creation with invalid password due to character requirements
def test_newUserInvalidCharacter(monkeypatch, capsys, freezeTime):
  clear()

  testPasswords = [
      "pytest123%", "PYTEST123", "aBcd&&&&", "999ZZZZ", "kop0`-2fwe"
  ]

  for testPassword in testPasswords:

    prompts = iter([{0: 'Sign Up'}, {0: 'Standard (free)'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, testPassword, defaultPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert "This password doesn't meet all the requirements." in capsys.readouterr().out
    assert readDB("users") == defaultUserTable
    clear()

# test new user creation with invalid password due to length requirements
def test_newUserInvalidLength(monkeypatch, capsys, freezeTime):
  clear()

  testPasswords = ["pyTes7!", "pyTest13!!!!!", "pyTestVeryLongPassword!"]

  for testPassword in testPasswords:
    # simulate inputs: choose Sign Up, provide a username and the test password, then provide a valid username and password combo to terminate the program

    prompts = iter([{0: 'Sign Up'}, {0: 'Standard (free)'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, testPassword, defaultPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    # test if the output informs the user of the invalid password
    assert "This password doesn't meet all the requirements." in capsys.readouterr().out

    # make sure no new users were added to the Users.txt file with invalid input
    assert readDB("users") == defaultUserTable
    clear()

# tests new user creation with existing username
def test_newUserInvalidExisting(monkeypatch, capsys, freezeTime):
  addTestUser()

  secondUser = list(defaultUserTuple)
  secondUser[0] = defaultUser+'1'

  prompts = iter([{0: 'Sign Up'}, {0: 'Standard (free)'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultUser+'1', defaultPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "This username is already taken." in capsys.readouterr().out
  assert readDB("users") == [[defaultUserTuple, tuple(secondUser)]]

# tests new user creation with maximum number of users
def test_newUserExceedsLimit(monkeypatch, capsys, freezeTime):
  comparison = addTestUser(maxUsers)

  # create the 6th account
  prompts = iter([{0: 'Sign Up'}, {0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  # Check if the expected error message is displayed to the user
  captured_output = capsys.readouterr().out
  assert "All permitted accounts have been created, please come back later" in captured_output
    
  assert comparison == readDB("users")

# tests existing user login with valid username/password
def test_loginExistingUser(monkeypatch, capsys, freezeTime):
  users = addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
  assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
  assert users == readDB("users")

# tests login attempt with invalid username.
def test_loginInvalidUsername(monkeypatch, capsys):
  addTestUser()
  
  testUsernames = ["pytestuser", "PYTESTUSER", "invaliduser", "1234567", ""]

  for testUsername in testUsernames:

    prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsername, defaultPassword, defaultUser, defaultPassword])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    captured_output = capsys.readouterr().out
    assert "\nIncorrect username / password, please try again\n" in captured_output

# tests login attempt with valid username but incorrect password
def test_loginInvalidPassword(monkeypatch, capsys):
  addTestUser()
  
  testPasswords = ["pyTest123", "pytest123%", "PYTEST123%", "pyTest12%", ""]

  for testPassword in testPasswords:

    prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, testPassword, defaultUser, defaultPassword])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    captured_output = capsys.readouterr().out
    assert "\nIncorrect username / password, please try again\n" in captured_output

# tests the post job feature
def test_postJob(monkeypatch, capsys, freezeTime):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Post a Job'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
  read = readDB("jobs")[0][0]
  assert read[1:5] == defaultJobTable[0][0][1:5] and read[7:9] == defaultJobTable[0][0][7:9]

# tests the post job feature when the next job would exceed the post limit
def test_postJobExceedsLimit(monkeypatch, capsys, freezeTime):
  addTestUser()

  jobs = [[]]
  for i in range(maxJobs):
     jobs[0].append((i+1, defaultUser, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary, defaultFirstName, defaultLastName, defaultDatePosted))
  
  addRowsToTable(jobs[0], 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Post a Job'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You have reached the maximum number of job postings." in capsys.readouterr().out
  read = readDB("jobs")[0][0]
  assert read[1:5] == defaultJobTable[0][0][1:5] and read[7:9] == defaultJobTable[0][0][7:9]

# tests the search skill feature
def test_searchSkill(monkeypatch, capsys):
  addTestUser()

  skills = ['Team Work', 'Clean Code', 'Customer Service', 'Marketing', 'Management']

  for skill in skills:

    prompts = iter([{0: 'Sign In'}, {0: 'Learn a new skill'}, {0: skill}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, defaultPassword])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"

# tests whether the sign in feature works from the useful links menu
def test_usefulLinksSignIn(monkeypatch, capsys, freezeTime):
  users = addTestUser()

  prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Sign Up'}, {0: 'Sign In'}, {0: 'Log out'}, {0: 'Back to General'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
  assert readDB("users") == users
  
# tests whether the sign up feature works from the useful links menu
def test_usefulLinksSignUp(monkeypatch, capsys, freezeTime):
  clear()

  testUsernamesPasswords = [["pyTestUser", "pyTest123%"],
                            ["pyTestUser2", "PYTEST123!"],
                            ["thisIsALongTestStringPyTestUser3", "1aBcd&&&&"],
                            ["4", "999ZZZZ^"], ["b", "kOp0`-2fwe"]]

  users = [[]]

  for testUsernamePassword in testUsernamesPasswords:

    prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Sign Up'}, {0: 'Sign Up'}, {0: 'Standard (free)'}, {0: 'Log out'}, {0: 'Back to General'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
    users[0].append((testUsernamePassword[0], hash(testUsernamePassword[1]), defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor, defaultTier, defaultCreationTime, defaultLastLogin)) 
    assert readDB("users") == users

def test_helpCenter(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Help Center'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "We're here to help." in capsys.readouterr().out

def test_about(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'About'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Welcome to In College, the world's largest college student network with many users in many countries and territories worldwide." in capsys.readouterr().out

def test_press(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Press'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "In College Pressroom: Stay on top of the latest news, updates, and reports." in capsys.readouterr().out

def test_blog(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Blog'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Under construction." in capsys.readouterr().out

def test_careers(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Careers'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Under construction." in capsys.readouterr().out

def test_developers(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Developers'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Under construction." in capsys.readouterr().out

def test_browse(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'Browse InCollege'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Under construction." in capsys.readouterr().out

def test_businessSolutions(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'Business Solutions'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Under construction." in capsys.readouterr().out

def test_directories(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'Useful Links'}, {0: 'Directories'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Under construction." in capsys.readouterr().out

###################
# Important Links #
###################

# tests the copyright notice feature
def test_copyrightNotice(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'InCollege Important Links'}, {0: 'A Copyright Notice'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "2023 InCollege" in capsys.readouterr().out

def test_aboutImportant(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'InCollege Important Links'}, {0: 'About'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "We're InCollege, a social networking solution made by college students for college students." in capsys.readouterr().out

def test_accessibility(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'InCollege Important Links'}, {0: 'Accessibility'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "InCollege is designed with navigation, readability, and usability, which benefits all users. By adding alt text to images and ensuring a logical content structure we have achieved to be ADA compliant and all users including those with disabilities can enjoy our services." in capsys.readouterr().out

def test_userAgreement(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'InCollege Important Links'}, {0: 'User Agreement'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Disclaimer: By using InCollege you agree to everything our policies say, including data being collected from you, the use of cookies on your computer, and copyright law applicable to you, among others. Please check our Privacy, Cookie, Copyright, and Brand policies for more detailed information." in capsys.readouterr().out

def test_privacyPolicy(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'InCollege Important Links'}, {0: 'Privacy Policy'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'},{0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
  assert "Current preferences (Emails: ON, SMS: ON, Advertising: ON)" in capsys.readouterr().out

def test_cookiePolicy(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'InCollege Important Links'}, {0: 'Cookie Policy'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Cookies are small data files that are placed on your computer or mobile device when you visit a website. Cookies are widely used by website owners in order to make their websites work, or to work more efficiently, as well as to provide reporting information. Cookies help us deliver our services, by using our services, you agree to our use of cookies in your computer." in capsys.readouterr().out

def test_copyrightPolicy(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'InCollege Important Links'}, {0: 'Copyright Policy'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Except as permitted by the copyright law applicable to you, you may not reproduce or communicate any of the content on this website, including files downloadable from this website, without the permission of the copyright owner." in capsys.readouterr().out

def test_brandPolicy(monkeypatch, capsys):
  clear()

  prompts = iter([{0: 'InCollege Important Links'}, {0: 'Brand Policy'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "InCollege understands how hard it is for students looking for a first job and will provide the tools that they need in order to be successful. Our goal is to continuously advance what's possibly in education and connect students from all around the world." in capsys.readouterr().out

def test_guestControlEmail(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'InCollege Important Links'}, {0: 'Guest Controls'}, {0: 'Email'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'no'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You will stop receiving InCollege emails" in capsys.readouterr().out
  assert readDB("users")[0][0][4] == False
  
def test_guestControlSMS(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'InCollege Important Links'}, {0: 'Guest Controls'}, {0: 'SMS'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'no'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You will stop receiving InCollege SMS's" in capsys.readouterr().out
  assert readDB("users")[0][0][5] == False

def test_guestControlAds(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'InCollege Important Links'}, {0: 'Guest Controls'}, {0: 'Advertising'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'no'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You will stop receiving InCollege advertising" in capsys.readouterr().out
  assert readDB("users")[0][0][6] == False

def test_language(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'InCollege Important Links'}, {0: 'Languages'}, {0: 'Spanish'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Language changed to Spanish" in capsys.readouterr().out
  assert readDB("users")[0][0][7] == "Spanish"

###########
# FRIENDS #
###########

def test_newConnectionRequest(monkeypatch, capsys):
  addTestUser(2)

  prompts = iter([{0: 'Sign In'}, {0: 'Find someone you know'}, {0: 'Last Name'}, {0: f'User ID: {defaultUser+"1"}, Name: {defaultFirstName} {defaultLastName}, University: {defaultUniversity}, Major: {defaultMajor}'}, {0: 'Exit'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultLastName, 'yes'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Connection request sent to user {defaultUser+'1'}!" in capsys.readouterr().out
  assert readDB("friendships")[0][0][3] == 'pending'

def test_receiveConnectionRequestOnLogin(monkeypatch, capsys):
  addTestUser(2)

  connections = [[(1, defaultUser+'1', defaultUser, 'pending')]]

  addRowsToTable(connections[0], 'friendships')

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'yes'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Friend request accepted!" in capsys.readouterr().out
  assert readDB("friendships")[0][0][3] == 'confirmed'

def test_disconnectFromConnectionEmpty(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'Disconnect from a Connection'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultUser])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"The given user is not in your connection list." in capsys.readouterr().out

def test_disconnectFromConnection(monkeypatch, capsys):
  addTestUser(2)
  
  connections = [[(1, defaultUser, defaultUser+'1', 'confirmed')]]

  addRowsToTable(connections[0], 'friendships')

  prompts = iter([{0: 'Sign In'}, {0: 'Disconnect from a Connection'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultUser+'1'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Successfully disconnected!" in capsys.readouterr().out 

def test_showMyNetworkEmpty(monkeypatch, capsys):
  addTestUser()
  
  prompts = iter([{0: 'Sign In'}, {0: 'Show my Network'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"You have no connections in the system." in capsys.readouterr().out

# change to a more robust assertion
def test_showMyNetwork(monkeypatch, capsys):
  addTestUser(2)

  connections = [[(1, defaultUser, defaultUser+'1', 'confirmed')]]
  
  addRowsToTable(connections[0], 'friendships')

  prompts = iter([{0: 'Sign In'}, {0: 'Show my Network'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "List of Friends:"\
       in capsys.readouterr().out

############################################ Sprint 5 Tests ###################################################

def test_addJobExperience(monkeypatch, capsys):
  # Test how the job experience is displayed
  addTestUser()
  mock_experience = [[1, defaultUser, 'Software Engineer', 'Tech Corp', '2022-01-01', '2022-12-31', 'New York', 'Developed software applications.']]
  mock_profile = [[1, defaultUser, "Title", "About section"]]
  addRowsToTable(mock_experience, "experiences")
  addRowsToTable(mock_profile, "profiles")

  prompts = iter([{0: 'Sign In'}, {0: 'Profile'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))
  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Worked as a Software Engineer for Tech Corp, from 2022-01-01 to 2022-12-31, at New York:" in capsys.readouterr().out 

def test_addEducation(monkeypatch, capsys):
  addTestUser()
  mock_education = [[1, defaultUser, "USF", "Computer Science", "2021", "2025"]]
  mock_profile = [[1, defaultUser, "Title", "About section"]]
  addRowsToTable(mock_education, "educations")
  addRowsToTable(mock_profile, "profiles")
  prompts = iter([{0: 'Sign In'}, {0: 'Profile'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))
  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Attended USF from 2021 to 2025 to obtain a Computer Science." in capsys.readouterr().out 


def test_createProfile(monkeypatch, capsys):
  addTestUser()
  
  prompts = iter([{0: 'Sign In'}, {0: 'Profile'}, {0: 'Create Profile'}, {0: 'Finish'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Profile Created" in capsys.readouterr().out
  assert readDB("profiles")[0][0][1] == defaultUser 

def test_editProfile(monkeypatch, capsys):
  addTestUser()

  profile = [[1, defaultUser, defaultProfileTitle, defaultProfileAbout]]
  addRowsToTable(profile, 'profiles')

  prompts = iter([{0: 'Sign In'}, {0: 'Profile'}, {0: 'Edit Profile'}, {0: 'Title'}, {0: 'Finish'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, "Title-example"])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Profile Edited" in capsys.readouterr().out
  assert readDB("profiles")[0][0][2] == "Title-example" 

def test_viewFriendEmptyProfile(monkeypatch, capsys):
  addTestUser(2)
  connections = [[1, defaultUser, defaultUser+"1", "confirmed"]]
  addRowsToTable(connections, "friendships")

  prompts = iter([{0: 'Sign In'}, {0: 'Show my Network'}, {0: f'User ID: {defaultUser+"1"}, Name: {defaultFirstName} {defaultLastName}'}, {0: 'View Profile'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"This user has not created a profile." in capsys.readouterr().out

def test_viewFriendProfile(monkeypatch, capsys):
  addTestUser(2)
  connections = [[1, defaultUser, defaultUser+"1", "confirmed"]]
  addRowsToTable(connections, "friendships")
  profile = [[1, defaultUser+"1", defaultProfileTitle, defaultProfileAbout]]
  addRowsToTable(profile, "profiles")

  prompts = iter([{0: 'Sign In'}, {0: 'Show my Network'}, {0: f'User ID: {defaultUser+"1"}, Name: {defaultFirstName} {defaultLastName} (View Profile)'}, {0: 'View Profile'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, "no"])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
  output = f"""
                    {defaultFirstName} {defaultLastName}
                    """ + f"""
                    {defaultProfileTitle}
                    """ + f"""
                    {defaultProfileAbout}
                    """ + f"""
                    University: {defaultUniversity}
                    Major: {defaultMajor}
                    """
  assert output in capsys.readouterr().out

############################################ Sprint 6 Tests ###################################################

def test_deleteJob(monkeypatch, capsys):
  addTestUser()
  jobs = [defaultJobTuple]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Delete a Job'}, {0: f"Job ID: 1, User ID: {defaultUser}, Title: {defaultTitle}, Description: {defaultDescription}, Employer: {defaultEmployer}, Location: {defaultLocation}, Salary: {defaultSalary}"}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert readDB('jobs') == [[]]

def test_deleteJobEmpty(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Delete a Job'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "No active job postings found." in capsys.readouterr().out

def test_searchJob(monkeypatch, capsys):
  addTestUser()
  jobs = [defaultJobTuple]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Go Back'}, {0: 'Go Back'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Job ID: 1 \nUser ID: {defaultUser} \nTitle: {defaultTitle}, \nDescription: {defaultDescription}, \nEmployer: {defaultEmployer}, \nLocation: {defaultLocation}, \nSalary: {defaultSalary}" in capsys.readouterr().out

def test_searchJobEmpty(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "No active job postings found." in capsys.readouterr().out

def test_saveJob(monkeypatch, capsys, freezeTime):
  addTestUser()
  jobs = [defaultJobTuple]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Save/Unsave the Job'}, {0: 'Go Back'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Job successfully saved" in capsys.readouterr().out
  assert readDB('saved_jobs')[0][0] == (defaultUser, 1, defaultFakeTime)

def test_unsaveJob(monkeypatch, capsys):
  addTestUser()
  jobs = [defaultJobTuple]
  addRowsToTable(jobs, 'jobs')
  saved_jobs = [(defaultUser, 1, defaultFakeTime)]
  addRowsToTable(saved_jobs, 'saved_jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Save/Unsave the Job'}, {0: 'Go Back'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Job successfully unsaved" in capsys.readouterr().out
  assert readDB('saved_jobs') == [[]]

def test_applyToJob(monkeypatch, capsys, freezeTime):
  addTestUser(2)
  jobPost = list(defaultJobTuple)
  jobPost[1] = defaultUser+'1'
  jobs = [jobPost]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Apply for the Job'}, {0: 'Go Back'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultApplicationDescription])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  dates = iter([defaultGraduationDate, defaultStartDate])
  monkeypatch.setattr('helper.getDate', lambda: next(dates))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Application submitted successfully!" in capsys.readouterr().out
  assert readDB('job_applications')[0][0] == defaultApplicationTuple

def test_applyToAppliedJob(monkeypatch, capsys):
  addTestUser()
  jobs = [defaultJobTuple]
  addRowsToTable(jobs, 'jobs')
  applications = [defaultApplicationTuple]
  addRowsToTable(applications, 'job_applications')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: f"Job ID: 1, Title: {defaultTitle} (Applied to)"}, {0: 'Apply for the Job'}, {0: 'Go Back'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultApplicationDescription])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  dates = iter([defaultGraduationDate, defaultStartDate])
  monkeypatch.setattr('helper.getDate', lambda: next(dates))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You have already applied for this job. You cannot apply again." in capsys.readouterr().out

def test_applyToOwnJob(monkeypatch, capsys):
  addTestUser()
  jobs = [defaultJobTuple]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Apply for the Job'}, {0: 'Go Back'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You cannot apply for a job you have posted." in capsys.readouterr().out

def test_listAppliedJobs(monkeypatch, capsys):
  addTestUser(2)
  jobPost = list(defaultJobTuple)
  jobPost[1] = defaultUser+'1'
  jobs = [jobPost]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, 
                  {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Apply for the Job'}, 
                  {0: 'Go Back'}, {0: 'List of Applied Jobs'}, {0: 'Back to the main menu'}, 
                  {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultApplicationDescription])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  dates = iter([defaultGraduationDate, defaultStartDate])
  monkeypatch.setattr('helper.getDate', lambda: next(dates))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "\nJobs Applied For:\n- Title: pyTester\n  Description: testsPython\n  Employer: pyTest\n  Location: pyTest\n  Salary: 0" in capsys.readouterr().out

def test_listUnappliedJobs(monkeypatch, capsys):
  addTestUser(2)
  jobPost = list(defaultJobTuple)
  jobPost[1] = defaultUser+'1'
  jobs = [jobPost]
  addRowsToTable(jobs, 'jobs')

  jobPost = list(defaultJobTuple)
  jobPost[0] = 2
  jobPost[1] = defaultUser+'1'
  jobPost[2] = defaultTitle+'2'
  jobs = [jobPost]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, 
                  {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Apply for the Job'}, 
                  {0: 'Go Back'}, {0: 'List not Applied Jobs'}, {0: 'Back to the main menu'}, 
                  {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultApplicationDescription])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  dates = iter([defaultGraduationDate, defaultStartDate])
  monkeypatch.setattr('helper.getDate', lambda: next(dates))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "\nJobs Not Yet Applied For:\n- Title: pyTester2\n  Description: testsPython\n  Employer: pyTest\n  Location: pyTest\n  Salary: 0" in capsys.readouterr().out

def test_listSavedJobs(monkeypatch, capsys):
  addTestUser(2)
  jobPost = list(defaultJobTuple)
  jobPost[1] = defaultUser+'1'
  jobs = [jobPost]
  addRowsToTable(jobs, 'jobs')

  jobPost = list(defaultJobTuple)
  jobPost[0] = 2
  jobPost[1] = defaultUser+'1'
  jobPost[2] = defaultTitle+'2'
  jobs = [jobPost]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, 
                  {0: f"Job ID: 1, Title: {defaultTitle}"}, {0: 'Save/Unsave the Job'}, 
                  {0: 'Go Back'}, {0: 'List of Saved Jobs'}, {0: 'Back to the main menu'}, 
                  {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  dates = iter([defaultGraduationDate, defaultStartDate])
  monkeypatch.setattr('helper.getDate', lambda: next(dates))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "\nSaved Jobs:\n- Title: pyTester\n  Description: testsPython\n  Employer: pyTest\n  Location: pyTest\n  Salary: 0" in capsys.readouterr().out

## Sprint 7 Tests ##

def test_sendMessage(monkeypatch, capsys, freezeTime):
  addTestUser(2)
  friendships = [[1, defaultUser, defaultUser+"1", "confirmed"]]
  addRowsToTable(friendships, "friendships")

  prompts = iter([{0: 'Sign In'}, {0: 'Messages'}, {0: 'Send Message'}, {0: f"User ID: {defaultUser+'1'}, Name: {defaultFirstName} {defaultLastName}"}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultMessage])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Message sent to user {defaultUser+'1'}!" in capsys.readouterr().out
  assert readDB("messages")[0] == [(1, defaultUser, defaultUser + '1', defaultMessage, "unread", defaultFakeTime)]

def test_sendMessageThroughNetwork(monkeypatch, capsys, freezeTime):
  clear()
  firstUser = list(defaultUserTuple)
  secondUser = list(defaultUserTuple)
  firstUser[10] = "Plus"
  secondUser[0] = defaultUser+'1'
  users = [tuple(firstUser), tuple(secondUser)]
  addRowsToTable(users, 'users')
  friendships = [[1, defaultUser, defaultUser+"1", "confirmed"]]
  addRowsToTable(friendships, "friendships")

  prompts = iter([{0: 'Sign In'}, {0: 'Show my Network'}, {0: f"User ID: {defaultUser+'1'}, Name: {defaultFirstName} {defaultLastName}"}, {0: 'Send Message'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultMessage])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Message sent to user {defaultUser+'1'}!" in capsys.readouterr().out
  assert readDB("messages")[0] == [(1, defaultUser, defaultUser + '1', defaultMessage, "unread", defaultFakeTime)]

def test_sendMessagePlus(monkeypatch, capsys, freezeTime):
  clear()
  firstUser = list(defaultUserTuple)
  secondUser = list(defaultUserTuple)
  firstUser[10] = "Plus"
  secondUser[0] = defaultUser+'1'
  users = [tuple(firstUser), tuple(secondUser)]
  addRowsToTable(users, 'users')

  prompts = iter([{0: 'Sign In'}, {0: 'Messages'}, {0: 'Send Message'}, {0: 'Show all students'}, {0: f"User ID: {defaultUser+'1'}, Name: {defaultFirstName} {defaultLastName}"}, {0: 'Go Back'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultMessage])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Message sent to user {defaultUser+'1'}!" in capsys.readouterr().out
  assert readDB("messages")[0] == [(1, defaultUser, defaultUser + '1', defaultMessage, "unread", defaultFakeTime)]

def test_messageNotificationOnLogin(monkeypatch, capsys):
  addTestUser(2)
  messages = [[1, defaultUser+'1', defaultUser, defaultMessage, "unread", defaultFakeTime]]
  addRowsToTable(messages, "messages")

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"You have messages waiting for you in your inbox." in capsys.readouterr().out

def test_readMessage(monkeypatch, capsys):
  addTestUser(2)
  messages = [[1, defaultUser+'1', defaultUser, defaultMessage, "unread", defaultFakeTime]]
  addRowsToTable(messages, "messages")

  prompts = iter([{0: 'Sign In'}, {0: 'Messages'}, {0: 'Inbox'}, {0: f'(UNREAD) {defaultFirstName} {defaultLastName}: {defaultMessage}'}, {0: 'Go Back'}, {0: 'Go Back'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert defaultMessage in capsys.readouterr().out
  assert readDB('messages')[0][0][4] == "read"

def test_deleteMessage(monkeypatch, capsys):
  addTestUser(2)
  messages = [[1, defaultUser+'1', defaultUser, defaultMessage, "unread", defaultFakeTime]]
  addRowsToTable(messages, "messages")

  prompts = iter([{0: 'Sign In'}, {0: 'Messages'}, {0: 'Inbox'}, {0: f'(UNREAD) {defaultFirstName} {defaultLastName}: {defaultMessage}'}, {0: 'Delete Message'}, {0: 'Go Back'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Message deleted." in capsys.readouterr().out
  assert readDB('messages') == [[]]

def test_respondToMessage(monkeypatch, capsys, freezeTime):
    addTestUser(2)
    messages = [[1, defaultUser+'1', defaultUser, defaultMessage, "unread", defaultFakeTime]]
    addRowsToTable(messages, "messages")

    prompts = iter([{0: 'Sign In'}, {0: 'Messages'}, {0: 'Inbox'}, {0: f'(UNREAD) {defaultFirstName} {defaultLastName}: {defaultConcatenatedMessage}'}, {0: 'Respond to Message'}, {0: 'Go Back'}, {0: 'Go Back'}, {0: 'Go Back'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, defaultPassword, defaultMessage])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert "Response message sent." in capsys.readouterr().out
    assert readDB('messages') == [[(1, defaultUser+'1', defaultUser, defaultMessage, "read", defaultFakeTime), (2, defaultUser, defaultUser+'1', defaultMessage, "unread", defaultFakeTime)]]

###
def test_notifyProfileNotCreated(monkeypatch, capsys):
  addTestUser()
  
  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Don't forget to create a profile" in capsys.readouterr().out

def test_notifyNewJobPosted(monkeypatch, capsys):
  addTestUser(2)
  jobs = list(defaultJobTuple)
  jobs[1] = defaultUser + '1'
  jobs[-1] += datetime.timedelta(0, 3)
  jobs = [jobs]
  addRowsToTable(jobs, 'jobs')

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"A new job {defaultTitle} has been posted by {defaultUser}" in capsys.readouterr().out

def test_notifyApplyForJobNoApplications(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Remember – you're going to want to have a job when you graduate. Make sure that you start to apply for jobs today!" in capsys.readouterr().out

def test_notifyApplyForJobSevenDays(monkeypatch, capsys):
  addTestUser(2)

  jobs = list(defaultJobTuple)
  jobs[1] = defaultUser + '1'
  jobs = [jobs]
  addRowsToTable(jobs, 'jobs')

  applications = list(defaultApplicationTuple)
  applications[-1] -= datetime.timedelta(7)
  applications = [applications]
  addRowsToTable(applications, 'job_applications')

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Remember – you're going to want to have a job when you graduate. Make sure that you start to apply for jobs today!" in capsys.readouterr().out

def test_notifyAppliedForNumJobs(monkeypatch, capsys):
  addTestUser(2)

  for i in (0, 1):
    if i == 1:
        jobs = list(defaultJobTuple)
        jobs[1] = defaultUser + '1'
        jobs = [jobs]
        addRowsToTable(jobs, 'jobs')
        applications = [defaultApplicationTuple]
        addRowsToTable(applications, 'job_applications')
      
    prompts = iter([{0: 'Sign In'}, {0: 'Job search/internship'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, defaultPassword])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert f"You have currently applied for {i} job(s)" in capsys.readouterr().out

def test_notifyAppliedJobDeleted(monkeypatch, capsys):
  addTestUser(2)

  applications = list(defaultApplicationTuple)
  applications[2] = None
  applications = [applications]
  addRowsToTable(applications, 'job_applications')

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"A job that you applied for has been deleted: {defaultTitle}" in capsys.readouterr().out

def test_notifyNewStudent(monkeypatch, capsys):
  clear()

  userTwo = list(defaultUserTuple)
  userTwo[0] += '1'
  userTwo[-2] += datetime.timedelta(0, 1)

  addRowsToTable([defaultUserTuple, userTwo], 'users')

  prompts = iter([{0: 'Sign In'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"{defaultFirstName} {defaultLastName} has joined InCollege" in capsys.readouterr().out

def test_dummy():
  dropTestDatabase()

# this has to be the last test in the file!