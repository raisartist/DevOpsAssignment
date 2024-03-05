import datetime
from forms import containsOnlyLetters, dateIsInThePast, integerIsValid, passwordIsValid, matchesEmailPattern

def test_contains_only_letters():
    valid_input = "OnlyLetters"
    invalid_input = "Not 0nly Letters"
    
    assert containsOnlyLetters(valid_input) == True
    assert containsOnlyLetters(invalid_input) == " Not 0nly Letters must only contain letters. "
    
def test_date_is_in_the_past():
    valid_date = datetime.date(2023,1,1)
    invalid_date = datetime.date(2000,1,1)
    
    assert dateIsInThePast(valid_date) == True
    assert dateIsInThePast(invalid_date) == " Date must be between 01/01/2019 and today. "
    
def test_integer_is_valid():
    min = 0
    max = 10
    valid_value = 5
    invalid_value = 12
    
    assert integerIsValid(valid_value, min, max) == True
    assert integerIsValid(invalid_value, min, max) == " Duration must be between 0 and 10 mins. "
    
def test_password_is_Valid():
    invalid_password = "0000"
    valid_password = "ABab123!?"
    
    assert passwordIsValid(valid_password) == True
    assert passwordIsValid(invalid_password) == " Invalid password: password must be 8-20 characters long with no spaces and include at least one lower case letter, one upper case letter, one digit and one special character (#,?,!,@,$,%,^,&,*,-). "
    
def test_matches_email_pattern():
    valid_email = "test@test.com"
    invalid_email = "test"
    
    assert matchesEmailPattern(valid_email) == True
    assert matchesEmailPattern(invalid_email) == " test is not a valid email. "
    