from enum import Enum

class Suggestion(Enum):
    union = "איחוד"
    split = "פיצול"

class Decision(Enum):
    yes = "כן"
    no = "לא"
    surveyor_decision = "?"

class surveyDecision(Enum):
    approved = "לקבל"
    reject = "לא לקבל"

class Notes(Enum):
    field_suggestion = "הצעה מהשטח"
    new_suggestion = "הצעה חדשה"
    pre_maping_suggestion_approved = "הצעה מקדם מיפוי – התקבלה"
    pre_maping_suggestion_rejected = "הצעה מקדם מיפוי – נדחתה"
    second_discussion_suggestion = "הצעה מהכנה לדיון שני"