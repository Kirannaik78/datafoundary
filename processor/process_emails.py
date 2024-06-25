import json
import os.path
from datetime import datetime
from models.emailModels import Email, SessionLocal

# path to rules json file
RULES_JSON = os.path.join(os.path.dirname(__file__), "../rules.json")
print(RULES_JSON)
def load_rules():
    """ load rules from json file """
    with open(RULES_JSON, 'r') as file:
        rules = json.load(file)
    return rules

def match_condition(email, condition):
    """check if an email match a condition based on json rules"""

    field = condition['field'] # field to match
    predicate = condition['predicate'] # condition predicate
    value = condition['value'] # value to match against

    # get the value of the email's field dynamically using getattr
    email_value = getattr(email, field.lower().replace(" ", "_"))

    if field == "received_datetime":
        # convert value to datetime object if comparing datetime
        email_value = email.received_datetime
        value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        if predicate == "less than":
            return email_value < value
        elif predicate == "greater than":
            return email_value > value

    # String comparison predicates
    if predicate == "contains":
        return value in email_value
    elif predicate == "does not contain":
        return value not in email_value
    elif predicate == "equals":
        return value == email_value
    elif predicate == "does not equal":
        return value != email_value

    return False # default to False if no match

def process_emails():
    """ Process emails based on loaded rules"""
    rules = load_rules() # load rules from json file
    db = SessionLocal() # get SQLAlchemy session

    emails = db.query(Email).all()

    # iterate through each eamil
    for email in emails:
        for rule in rules:
            conditions_met = []
            # check each condition in the rule against the current email
            for condition in rule['conditions']:
                if match_condition(email, condition):
                    conditions_met.append(True) # condition is met
                else:
                    conditions_met.append(False) # condition is not met
            # check if all conditions in 'All' or any condition in 'any' rule are met
            if (rule['predicate'] == 'All' and all(conditions_met)) or (rule['predicate'] == 'Any' and any(conditions_met)):
                for action in rule['actions']:
                    if action == "mark_as_read":
                        # updating database with column is_read with true
                        print(f"Marking email {email.id} as read")
                        email.is_read = True  # Assuming a field 'is_read' in Email model
                    elif action == "move_message":
                        # update column folder to archive
                        print(f"Moving email {email.id} to folder")
                        email.folder = "Archive"  # Example: Moving to an 'Archive' folder

    db.commit() # commit changes to the database
    db.close() # close the database session

if __name__ == "__main__":
    process_emails()
