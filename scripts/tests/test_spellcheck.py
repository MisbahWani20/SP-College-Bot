
from chatbot.spellcheck import find_closest_subject


test_cases = [


    ("english", "English"),
    ("engish", "English"),
    ("englsh", "English"),
    ("englsh", "English"),

    ("economics", "Economics"),
    ("econmics", "Economics"),
    ("economcs", "Economics"),
    ("economic", "Economics"),

    ("political science", "Political Science"),
    ("politcal science", "Political Science"),
    ("political scince", "Political Science"),
    ("poltical science", "Political Science"),

    ("history", "History"),
    ("histroy", "History"),
    ("histry", "History"),
    ("histor", "History"),

    ("sociology", "Sociology"),
    ("socilogy", "Sociology"),
    ("sociolgy", "Sociology"),
    ("sociologyy", "Sociology"),

    ("psychology", "Psychology"),
    ("psycology", "Psychology"),
    ("psychlogy", "Psychology"),
    ("psycholgy", "Psychology"),

    ("education", "Education"),
    ("educaton", "Education"),
    ("educatin", "Education"),
    ("eduction", "Education"),

    ("arabic", "Arabic"),
    ("arabc", "Arabic"),
    ("arabi", "Arabic"),

    ("urdu", "Urdu"),
    ("urd", "Urdu"),

    ("kashmiri", "Kashmiri"),
    ("kashmri", "Kashmiri"),
    ("kashmiri", "Kashmiri"),

    ("philosophy", "Philosophy"),
    ("philosphy", "Philosophy"),
    ("philosohy", "Philosophy"),
    ("philosopy", "Philosophy"),

    ("public administration", "Public Administration"),
    ("public administrtion", "Public Administration"),
    ("publc administration", "Public Administration"),
    ("public adminstration", "Public Administration"),

    ("islamic studies", "Islamic Studies"),
    ("islamic studes", "Islamic Studies"),
    ("islamc studies", "Islamic Studies"),
    ("islamic studies", "Islamic Studies"),

    ("music", "Music"),
    ("msic", "Music"),
    ("musc", "Music"),

    ("social work", "Social Work"),
    ("socail work", "Social Work"),
    ("social wrk", "Social Work"),
    ("socil work", "Social Work"),

    ("geography", "Geography"),
    ("geogrpahy", "Geography"),
    ("geogaphy", "Geography"),
    ("geograpy", "Geography"),

    ("geography arts", "Geography (Arts)"),
    ("geography arts", "Geography (Arts)"),
    ("geograpy arts", "Geography (Arts)"),


    ("physics", "Physics"),
    ("physic", "Physics"),
    ("physis", "Physics"),
    ("phisics", "Physics"),
    ("phyics", "Physics"),
    ("physcs", "Physics"),
    ("physicss", "Physics"),

    ("chemistry", "Chemistry"),
    ("chem", "Chemistry"),
    ("chmistry", "Chemistry"),
    ("chemstry", "Chemistry"),
    ("chemsitry", "Chemistry"),
    ("chemisty", "Chemistry"),

    ("mathematics", "Mathematics"),
    ("mathematic", "Mathematics"),
    ("mathematicss", "Mathematics"),
    ("mathemetics", "Mathematics"),
    ("mathmatics", "Mathematics"),
    ("mathematcs", "Mathematics"),

    ("botany", "Botany"),
    ("botny", "Botany"),
    ("botanyy", "Botany"),
    ("btany", "Botany"),

    ("zoology", "Zoology"),
    ("zoolgy", "Zoology"),
    ("zoology", "Zoology"),
    ("zoloy", "Zoology"),

    ("biotechnology", "Biotechnology"),
    ("biotechology", "Biotechnology"),
    ("biotechnlogy", "Biotechnology"),
    ("biotechnolgy", "Biotechnology"),

    ("environmental science", "Environmental Science"),
    ("environmetal science", "Environmental Science"),
    ("environmental scince", "Environmental Science"),
    ("enviromental science", "Environmental Science"),

    ("information technology", "Information Technology"),
    ("information tecnology", "Information Technology"),
    ("informtion technology", "Information Technology"),
    ("information technolog", "Information Technology"),

    ("biochemistry", "Bio-Chemistry"),
    ("biochemstry", "Bio-Chemistry"),
    ("biochemisty", "Bio-Chemistry"),
    ("bio chemistry", "Bio-Chemistry"),

    ("clinical biochemistry", "Clinical Biochemistry"),
    ("clinical biochemstry", "Clinical Biochemistry"),
    ("clinical biochemisty", "Clinical Biochemistry"),
    ("clincal biochemistry", "Clinical Biochemistry"),

    ("statistics", "Statistics"),
    ("statistcs", "Statistics"),
    ("statitics", "Statistics"),
    ("statisics", "Statistics"),

    ("geology", "Geology"),
    ("geolgy", "Geology"),
    ("geolgoy", "Geology"),
    ("geoloy", "Geology"),

    ("electronics", "Electronics"),
    ("electonics", "Electronics"),
    ("electroncs", "Electronics"),
    ("electonic", "Electronics"),

    ("water management", "Water Management"),
    ("water managment", "Water Management"),
    ("wter management", "Water Management"),
    ("water managemnt", "Water Management"),

    ("food science technology", "Food Science & Technology"),
    ("food science and technology", "Food Science & Technology"),
    ("food scince technology", "Food Science & Technology"),
    ("food science technolog", "Food Science & Technology"),

    ("home science", "Home Science"),
    ("home scince", "Home Science"),
    ("hme science", "Home Science"),
    ("home sciense", "Home Science"),


    (
        "journalism mass communication",
        "Journalism & Mass Communication"
    ),

    (
        "journalim mass communication",
        "Journalism & Mass Communication"
    ),

    (
        "journalism mass comunication",
        "Journalism & Mass Communication"
    ),

    (
        "journalism and mass communication",
        "Journalism & Mass Communication"
    ),

    (
        "journalism mass communication hons",
        "Journalism & Mass Communication Hons"
    ),

    (
        "journalim mass communication hons",
        "Journalism & Mass Communication Hons"
    ),



    ("business administration", "Business Administration (BBA/MBA)"),
    ("business adminstration", "Business Administration (BBA/MBA)"),
    ("business administrtion", "Business Administration (BBA/MBA)"),

    ("commerce", "Commerce(BCom-MCom)"),
    ("comerce", "Commerce(BCom-MCom)"),
    ("comerce bcom mcom", "Commerce(BCom-MCom)"),

    ("computer applications", "Computer Applications (BCA/MCA)"),
    ("computer aplications", "Computer Applications (BCA/MCA)"),
    ("computr applications", "Computer Applications (BCA/MCA)"),
    ("computer application", "Computer Applications (BCA/MCA)"),

    ("artificial intelligence machine learning",
     "Artificial Intelligence & Machine Learning"),

    ("artifical intelligence machine learning",
     "Artificial Intelligence & Machine Learning"),

    ("artificial inteligence machine learning",
     "Artificial Intelligence & Machine Learning"),

    ("artificial intelligence and machine learning",
     "Artificial Intelligence & Machine Learning"),

    ("data science", "Data Science"),
    ("data scince", "Data Science"),
    ("dat science", "Data Science"),
    ("data sciense", "Data Science"),

 

    ("regular", "Regular"),
    ("reglar", "Regular"),

    ("general", "General"),
    ("genral", "General"),

    ("hons", "Hons"),
    ("hon", "Hons"),

    ("bcom hons", "Bcom Hons"),
    ("bcom hon", "Bcom Hons"),
    ("bcom hons", "Bcom Hons"),

    ("biochemistry hons", "Biochemistry Hons"),
    ("biochemstry hons", "Biochemistry Hons"),
    ("biochemistry hon", "Biochemistry Hons"),

    ("economics hons", "Economics Hons"),
    ("econmics hons", "Economics Hons"),
    ("economics hon", "Economics Hons"),
]

test_words = [



    "food science technology",
    "food science and technology",
    "food science & technology",
    "food scince technology",
    "food science technolog",

    "artificial intelligence machine learning",
    "artificial intelligence and machine learning",
    "artificial intelligence & machine learning",
    "artifical intelligence machine learning",
    "artificial inteligence machine learning",



    "journalism mass communication",
    "journalism and mass communication",
    "journalism & mass communication",
    "journalim mass communication",
    "journalism mass comunication",

]




total = 0
passed = 0
failed = 0


for word, expected in test_cases:

    total += 1

    subject, score = find_closest_subject(word)

    is_pass = (
        subject is not None
        and subject.lower() == expected.lower()
    )

    if is_pass:
        passed += 1
    else:
        failed += 1

    print("\nInput:", word)
    print("Expected:", expected)
    print("Match:", subject)
    print("Score:", round(score, 3))
    print("Result:", "PASS" if is_pass else "FAIL")



print("\n")
print("=" * 50)
print("SPELLCHECK TEST SUMMARY")
print("=" * 50)
print("Total Tests :", total)
print("Passed      :", passed)
print("Failed      :", failed)

if failed == 0:
    print("Overall     : ALL TESTS PASSED")
else:
    print("Overall     : SOME TESTS FAILED")

print("=" * 50)

