import main, pytest, psycopg, helper
from main import DATABASE_NAME_, InCollegeServer

# TODO: update comments to reflect change from .txt file to database

# these functions are for managing the Users.txt file; we don't want the file to be altered in any way after the tests are completed and we don't want the test output to rely on the existing file being in a certain state.
# so we start by saving the Users.txt contents to a string and erasing it. At the start of every test, we erase it again (to clear any alterations from previous tests) and the final test (see test_dummy) writes the string back to the Users.txt file

sourceFilename = 'main'
promptModule = sourceFilename + '.prompt'

defaultUser = "pyTestUser"
defaultPassword = "pyTest123%"
defaultFirstName = "pyTest"
defaultLastName = "User"
defaultEmailPref = True
defaultSMSPref = True
defaultAdsPref = True
defaultLanguage = "English"
defaultUniversity = "USF"
defaultMajor = "CS"
defaultUserTuple = (defaultUser, defaultPassword, defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor)
defaultUserTupleString = f"('{defaultUser}', '{defaultPassword}', '{defaultFirstName}', '{defaultLastName}', {defaultEmailPref}, {defaultSMSPref}, {defaultAdsPref}, '{defaultLanguage}', '{defaultUniversity}', '{defaultMajor}')"
defaultUserTable = [[defaultUserTuple]]
maxUsers = 10

# TODO: change queries that rely on the string method to use cursor.copy()

defaultTitle = "pyTester"
defaultDescription = "testsPython"
defaultEmployer = "pyTest"
defaultLocation = "pyTest"
defaultSalary = "0"
defaultJobTuple = (1, defaultUser, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary, defaultFirstName, defaultLastName)
defaultJobTable = [[defaultJobTuple]]
maxJobs = 5

tables = ["jobs", "friendships", "users"] # this needs to be in an order such that the tables with linked keys are deleted first

DATABASE_TEST_NAME = "incollegetestdb"
DATABASE_ORIGINAL = DATABASE_NAME_

DATABASE_NAME = DATABASE_TEST_NAME
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"
DATABASE_HOST = "localhost" 
DATABASE_PORT = "5432"

def dropTestDatabase():
    with psycopg.connect(dbname=DATABASE_ORIGINAL, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
       connection._set_autocommit(True)
       with connection.cursor() as cursor:
          cursor.execute(f"""DROP DATABASE {DATABASE_TEST_NAME};""")

def clear():
    with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
        with connection.cursor() as cursor:
            for table in tables:
                try:
                    cursor.execute(f"""DELETE FROM {table}""")
                except Exception as e:
                    print(f"Error executing query: {e}")
            cursor.execute("""ALTER SEQUENCE jobs_job_id_seq RESTART WITH 1""")

# function to start tests which require an existing user to be able to log in
# don't use this function unless you need an existing user! start the function with clear() instead
def addTestUser(num = 1):
  clear()
  finalTuple = [[]]

  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
        with connection.cursor() as cursor:
              try:
                  cursor.execute(f"""INSERT INTO USERS VALUES {defaultUserTupleString}""")
                  finalTuple[0].append(defaultUserTuple)
              except Exception as e:
                  print(f"Error executing query: {e}")
              if num > 1:
                 for i in range(1, num):
                    userTupleString = f"('{defaultUser}{str(i)}', '{defaultPassword}', '{defaultFirstName}', '{defaultLastName}', {defaultEmailPref}, {defaultSMSPref}, {defaultAdsPref}, '{defaultLanguage}', '{defaultUniversity}', '{defaultMajor}')"
                    userTuple = (defaultUser+str(i), defaultPassword, defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor)
                    try:
                      cursor.execute(f"""INSERT INTO USERS VALUES {userTupleString}""")
                      finalTuple[0].append(userTuple)
                    except Exception as e:
                        print(f"Error executing query: {e}")
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
              for table in tables:
                  try:
                      cursor.execute(f"""SELECT *
                                      FROM {table}""")
                      read.append(cursor.fetchall())
                  except Exception as e:
                      print(f"Error executing query: {e}")
    return read

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

  prompts = iter([{0: 'To Find an Existing User'}, {0: 'Last Name'}, {0: 'Exit'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultLastName])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"User found in the InCollege system.\n\nUser ID: {defaultUser}, Name: {defaultFirstName} {defaultLastName}, University: {defaultUniversity}, Major: {defaultMajor}"\
          in capsys.readouterr().out

def test_mainScreenSearchUserByUniversity(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'To Find an Existing User'}, {0: 'University'}, {0: 'Exit'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUniversity])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"User found in the InCollege system.\n\nUser ID: {defaultUser}, Name: {defaultFirstName} {defaultLastName}, University: {defaultUniversity}, Major: {defaultMajor}"\
          in capsys.readouterr().out

def test_mainScreenSearchUserByMajor(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'To Find an Existing User'}, {0: 'Major'}, {0: 'Exit'}, {0: 'Exit'}])
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

    prompts = iter([{0: 'To Find an Existing User'}, {0: 'Last Name'}, {0: 'Exit'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testName])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert f"No user found with Last Name: {testName}." in capsys.readouterr().out

# tests new user creation with valid username/password
def test_newUser(monkeypatch, capsys):
  clear()

  testUsernamesPasswords = [["pyTestUser", "pyTest123%"],
                            ["pyTestUser2", "PYTEST123!"],
                            ["thisIsALongTestStringPyTestUser3", "1aBcd&&&&"],
                            ["4", "999ZZZZ^"], ["b", "kOp0`-2fwe"]]

  users = [[]]

  for testUsernamePassword in testUsernamesPasswords:

    prompts = iter([{0: 'To Create an Account'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
    users[0].append((testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor))
    assert readDB("users") == users

# tests new user creation with invalid password due to character requirements
def test_newUserInvalidCharacter(monkeypatch, capsys):
  clear()

  testPasswords = [
      "pytest123%", "PYTEST123", "aBcd&&&&", "999ZZZZ", "kop0`-2fwe"
  ]

  for testPassword in testPasswords:

    prompts = iter([{0: 'To Create an Account'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, testPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor, defaultUser, defaultPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert "Your username is already taken or the password doesn't meet requirements. Please start over" in capsys.readouterr().out
    assert readDB("users") == defaultUserTable
    clear()

# test new user creation with invalid password due to length requirements
def test_newUserInvalidLength(monkeypatch, capsys):
  clear()

  testPasswords = ["pyTes7!", "pyTest13!!!!!", "pyTestVeryLongPassword!"]

  for testPassword in testPasswords:
    # simulate inputs: choose to create an account, provide a username and the test password, then provide a valid username and password combo to terminate the program

    prompts = iter([{0: 'To Create an Account'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, testPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor, defaultUser, defaultPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    # test if the output informs the user of the invalid password
    assert "Your username is already taken or the password doesn't meet requirements. Please start over" in capsys.readouterr().out

    # make sure no new users were added to the Users.txt file with invalid input
    assert readDB("users") == defaultUserTable
    clear()

# tests new user creation with existing username
# kind of an inelegant implementation but works
def test_newUserInvalidExisting(monkeypatch, capsys):
  clear()

  testUsernames = [
      "pyTestUser1", "pyTestUser2", "thisIsALongTestStringPyTestUser3", "4"
  ]

  users = [[]]

  for testUsername in testUsernames:
    users[0].append((testUsername, defaultPassword, defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor))

  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    with connection.cursor() as cursor:
      try:
          with cursor.copy("COPY users FROM STDIN") as copy:
                for user in users[0]:
                  copy.write_row(user)
      except Exception as e:
          print(f"Error executing query: {e}")

  for testUsername in testUsernames:

    prompts = iter([{0: 'To Create an Account'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsername, defaultPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor, defaultUser, defaultPassword, defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
    users[0].append(defaultUserTuple)
    assert users == readDB("users")
    users[0].pop()

# tests new user creation with maximum number of users
def test_newUserExceedsLimit(monkeypatch, capsys):
  comparison = addTestUser(maxUsers)

  # create the 6th account
  prompts = iter([{0: 'To Create an Account'}, {0: 'For Existing Users'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  # Check if the expected error message is displayed to the user
  captured_output = capsys.readouterr().out
  assert "All permitted accounts have been created, please come back later" in captured_output
    
  assert comparison == readDB("users")

# tests existing user login with valid username/password
def test_loginExistingUser(monkeypatch, capsys):
  clear()

  testUsernamesPasswords = [["pyTestUser", "pytest123%"],
                            ["pyTestUser2", "PYTEST123"],
                            ["thisIsALongTestStringPyTestUser3", "aBcd&&&&"],
                            ["4", "999ZZZZ"], ["b", "kop0`-2fwe"]]

  users = [[]]

  for testUsernamePassword in testUsernamesPasswords:
    users[0].append((testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor))

  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    with connection.cursor() as cursor:
      try:
          with cursor.copy("COPY users FROM STDIN") as copy:
                for user in users[0]:
                  copy.write_row(user)
      except Exception as e:
          print(f"Error executing query: {e}")

  for testUsernamePassword in testUsernamesPasswords:

    prompts = iter([{0: 'For Existing Users'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
    assert users == readDB("users")

# tests login attempt with invalid username.
def test_loginInvalidUsername(monkeypatch, capsys):
  addTestUser()
  
  testUsernames = ["pytestuser", "PYTESTUSER", "invaliduser", "1234567", ""]

  for testUsername in testUsernames:

    prompts = iter([{0: 'For Existing Users'}, {0: 'Log out'}, {0: 'Exit'}])
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

    prompts = iter([{0: 'For Existing Users'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, testPassword, defaultUser, defaultPassword])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    captured_output = capsys.readouterr().out
    assert "\nIncorrect username / password, please try again\n" in captured_output

""" deprecated tests, test for friend function instead

# tests the search user function
def test_searchUser(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'For Existing Users'}, {0: 'Find someone you know'}, {0: 'Last Name'}, {0: 'Exit'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultLastName])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "They are a part of the InCollege system." in capsys.readouterr().out

# tests the search user function with a name that is not registered with inCollege
def test_searchInvalidUser(monkeypatch, capsys):
  addTestUser()

  testNames = [["User", "pyTest"], ["pyTest", ""], ["", "User"], ["", ""]]

  for testName in testNames:

    prompts = iter([{0: 'For Existing Users'}, {0: 'Find someone you know'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, defaultPassword, testName[0], testName[1]])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert "They are not yet a part of the InCollege system yet." in capsys.readouterr().out

"""
    
# tests the search job feature
def test_searchJob(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'For Existing Users'}, {0: 'Job search/internship'}, {0: 'Search for a Job'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "under construction." in capsys.readouterr().out

# tests the post job feature
def test_postJob(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'For Existing Users'}, {0: 'Job search/internship'}, {0: 'Post a Job'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
  read = readDB("jobs")[0][0]
  assert read[1:5] == defaultJobTable[0][0][1:5] and read[7:8] == defaultJobTable[0][0][7:8]

# tests the post job feature when the next job would exceed the post limit
def test_postJobExceedsLimit(monkeypatch, capsys):
  addTestUser()

  jobs = [[]]
  for i in range(maxJobs):
     jobs[0].append((i+1, defaultUser, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary, defaultFirstName, defaultLastName))
  
  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    with connection.cursor() as cursor:
      try:
        with cursor.copy("COPY jobs FROM STDIN") as copy:
          for job in jobs[0]:
            copy.write_row(job)
      except Exception as e:
        print(f"Error executing query: {e}")     

  prompts = iter([{0: 'For Existing Users'}, {0: 'Job search/internship'}, {0: 'Post a Job'}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultTitle, defaultDescription, defaultEmployer, defaultLocation, defaultSalary])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You have reached the maximum number of job postings." in capsys.readouterr().out
  read = readDB("jobs")[0][0]
  assert read[1:5] == defaultJobTable[0][0][1:5] and read[7:8] == defaultJobTable[0][0][7:8]

# tests the search skill feature
def test_searchSkill(monkeypatch, capsys):
  addTestUser()

  skills = ['Team Work', 'Clean Code', 'Customer Service', 'Marketing', 'Management']

  for skill in skills:

    prompts = iter([{0: 'For Existing Users'}, {0: 'Learn a new skill'}, {0: skill}, {0: 'Back to the main menu'}, {0: 'Log out'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([defaultUser, defaultPassword])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"

# tests whether the sign in feature works from the useful links menu
def test_usefulLinksSignIn(monkeypatch, capsys):
  clear()

  testUsernamesPasswords = [["pyTestUser", "pytest123%"],
                            ["pyTestUser2", "PYTEST123"],
                            ["thisIsALongTestStringPyTestUser3", "aBcd&&&&"],
                            ["4", "999ZZZZ"], ["b", "kop0`-2fwe"]]

  users = [[]]

  for testUsernamePassword in testUsernamesPasswords:
    users[0].append((testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor))

  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    with connection.cursor() as cursor:
      try:
        with cursor.copy("COPY users FROM STDIN") as copy:
          for user in users[0]:
            copy.write_row(user)
      except Exception as e:
          print(f"Error executing query: {e}")

  for testUsernamePassword in testUsernamesPasswords:

    prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Sign Up'}, {0: 'For Existing User'}, {0: 'Log out'}, {0: 'Back to General'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsernamePassword[0], testUsernamePassword[1]])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
    assert readDB("users") == users
  
# tests whether the sign up feature works from the useful links menu
def test_usefulLinksSignUp(monkeypatch, capsys):
  clear()

  testUsernamesPasswords = [["pyTestUser", "pyTest123%"],
                            ["pyTestUser2", "PYTEST123!"],
                            ["thisIsALongTestStringPyTestUser3", "1aBcd&&&&"],
                            ["4", "999ZZZZ^"], ["b", "kOp0`-2fwe"]]

  users = [[]]

  for testUsernamePassword in testUsernamesPasswords:

    prompts = iter([{0: 'Useful Links'}, {0: 'General'}, {0: 'Sign Up'}, {0: 'To Create an Account'}, {0: 'Log out'}, {0: 'Back to General'}, {0: 'Back to Useful Links'}, {0: 'Back to Main Menu'}, {0: 'Exit'}])
    monkeypatch.setattr(promptModule, lambda _: next(prompts))

    inputs = iter([testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultUniversity, defaultMajor])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    assert capsys.readouterr().out.split('\n')[-3] == "Thank you, bye!"
    users[0].append((testUsernamePassword[0], testUsernamePassword[1], defaultFirstName, defaultLastName, defaultEmailPref, defaultSMSPref, defaultAdsPref, defaultLanguage, defaultUniversity, defaultMajor)) 
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

  prompts = iter([{0: 'For Existing Users'}, {0: 'InCollege Important Links'}, {0: 'Privacy Policy'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'},{0: 'Log out'}, {0: 'Exit'}])
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

  prompts = iter([{0: 'For Existing Users'}, {0: 'InCollege Important Links'}, {0: 'Guest Controls'}, {0: 'Email'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'no'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You will stop receiving InCollege emails" in capsys.readouterr().out
  assert readDB("users")[0][0][4] == False
  
def test_guestControlSMS(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'For Existing Users'}, {0: 'InCollege Important Links'}, {0: 'Guest Controls'}, {0: 'SMS'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'no'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You will stop receiving InCollege SMS's" in capsys.readouterr().out
  assert readDB("users")[0][0][5] == False

def test_guestControlAds(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'For Existing Users'}, {0: 'InCollege Important Links'}, {0: 'Guest Controls'}, {0: 'Advertising'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'no'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "You will stop receiving InCollege advertising" in capsys.readouterr().out
  assert readDB("users")[0][0][6] == False

def test_language(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'For Existing Users'}, {0: 'InCollege Important Links'}, {0: 'Languages'}, {0: 'Spanish'}, {0: 'Back to Important Links'}, {0: 'Back to Main Menu'}, {0: 'Log out'}, {0: 'Exit'}])
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

  prompts = iter([{0: 'For Existing Users'}, {0: 'Find someone you know'}, {0: 'Last Name'}, {0: f'User ID: {defaultUser+"1"}, Name: {defaultFirstName} {defaultLastName}, University: {defaultUniversity}, Major: {defaultMajor}'}, {0: 'Exit'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultLastName, 'yes'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Connection request sent to user {defaultUser+'1'}!" in capsys.readouterr().out
  assert readDB("friendships")[0][0][3] == 'pending'

def test_receiveConnectionRequestOnLogin(monkeypatch, capsys):
  addTestUser(2)

  connections = [[(1, defaultUser+'1', defaultUser, 'pending')]]

  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    with connection.cursor() as cursor:
      try:
        with cursor.copy("COPY friendships FROM STDIN") as copy:
          for connection in connections[0]:
            copy.write_row(connection)
      except Exception as e:
          print(f"Error executing query: {e}")

  prompts = iter([{0: 'For Existing Users'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, 'yes'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert "Friend request accepted!" in capsys.readouterr().out
  assert readDB("friendships")[0][0][3] == 'confirmed'

def test_disconnectFromConnectionEmpty(monkeypatch, capsys):
  addTestUser()

  prompts = iter([{0: 'For Existing Users'}, {0: 'Disconnect from a Connection'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultUser])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"The given user is not in your connection list." in capsys.readouterr().out

def test_disconnectFromConnection(monkeypatch, capsys):
  addTestUser(2)
  
  connections = [[(1, defaultUser, defaultUser+'1', 'confirmed')]]

  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    with connection.cursor() as cursor:
      try:
        with cursor.copy("COPY friendships FROM STDIN") as copy:
          for connection in connections[0]:
            copy.write_row(connection)
      except Exception as e:
          print(f"Error executing query: {e}")

  prompts = iter([{0: 'For Existing Users'}, {0: 'Disconnect from a Connection'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword, defaultUser+'1'])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"Successfully disconnected!" in capsys.readouterr().out 

def test_showMyNetworkEmpty(monkeypatch, capsys):
  addTestUser()
  
  prompts = iter([{0: 'For Existing Users'}, {0: 'Show my Network'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"You have no connections in the system." in capsys.readouterr().out

def test_showMyNetwork(monkeypatch, capsys):
  addTestUser(2)

  connections = [[(1, defaultUser, defaultUser+'1', 'confirmed')]]
  
  with psycopg.connect(dbname=DATABASE_TEST_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT) as connection:
    with connection.cursor() as cursor:
      try:
        with cursor.copy("COPY friendships FROM STDIN") as copy:
          for connection in connections[0]:
            copy.write_row(connection)
      except Exception as e:
          print(f"Error executing query: {e}")

  prompts = iter([{0: 'For Existing Users'}, {0: 'Show my Network'}, {0: 'Log out'}, {0: 'Exit'}])
  monkeypatch.setattr(promptModule, lambda _: next(prompts))

  inputs = iter([defaultUser, defaultPassword])
  monkeypatch.setattr('builtins.input', lambda _: next(inputs))

  InCollegeServer(DATABASE_TEST_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)

  assert f"List of Friends:\nUser ID: {defaultUser+'1'}, Name: {defaultFirstName} {defaultLastName}"\
       in capsys.readouterr().out

# workaround for pytest terminating after the last test function; userPaste needs to be called to recover the original data in Users.txt

def test_dummy():
  dropTestDatabase()

# this has to be the last test in the file!