def contains_any(question, words):
    question = question.lower()
    return any(word in question for word in words)

INTAKE = [
    "seat",
    "seats",
    "intake",
    "capacity",
    "available seats",
    "total seats",
    "strength"

]

FEE = [
    "fee",
    "fees",
    "cost",
    "costs",
    "charges",
    "tuition",
    "payment",
    "price",
    "how much",
    "how much does",
    "how much is",
    "what does it cost",
    "what is the fee",
    "what are the fees"

]

ELIGIBILITY = [
    "eligibility",
    "eligible",
    "qualification",
    "criteria",
    "requirements",
    "required"

]


DURATION = [
    "duration",
    "year",
    "years",
    "semester",
    "semesters",
    "time",
    "period",
    "how long",
    "how many years",
    "how many year",
    "length of the programme",
    "length of programme",
    "how long does",
    "how long is",
    "how many years does this course take",
    "how many years does this programme take",
    "how long does this course take",
    "how long does this programme take"

]

DEPARTMENT = [
    "department",
    "dept",
    "school",
    "faculty"
]

ADMISSION = [
    "admission",
    "apply",
    "application",
    "admission process"
]

ENTRANCE = [
    "entrance exam",
    "entrance test",
    "entrance examination",
    "entrance",
    "cuset",
    "cuet",
    "entrance requirement",
    "entrance requirements",
    "entrance criteria",
    "test required",
    "exam required",
    "exam requirement",
    "exam requirements"
]

SELECTION = [
    "selection",
    "selection process",
    "selection criteria"
]

COLLEGE = [
    "college",
    "offered",
    "offers",
    "where",
    "campus"

]


OVERVIEW = [

    "about",
    "overview",
    "details",
    "information",
    "tell me",
    "explain"

]