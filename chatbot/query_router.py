def detect_query_type(question):
    question = question.lower()
    print(question)

    if "integrated" in question:    
        return "programme"

    programme_keywords = [
    # UG
      "ba","bsc","bcom","bca","bba",

    # Integrated
      "integrated","integrated msc","integrated ma",
      "integrated mba","integrated mca","msc","chemistry",
      "bed","b.ed","med","m.ed",

    # PG
      "ma","msc","mcom","mba","mca",

    # General
      "programme","program","course","courses",
      "specialization","school",

    # Programme information
      "eligibility","fee","fees","intake","seat","seats",
      "duration","selection",
    #   "admission",
    #   "admission process",
    #   "selection process",
      "cuet",
      "study",
      "studied",
      "where can i study",
      "where to study",
      "information technology",
      "it",
      "computer applications",
      "computer science",
      "data science",
      "physics",
      "chemistry",
      "geography",
      "mathematics",
      "botany",
      "zoology",
      "economics",
      "english",
      "history",
      "psychology",
      "statistics",
      "biotechnology",
      "biochemistry",
      "environmental science",
      "urdu",
      "education"
    ]

    pdf_keywords = [
        "policy",
        "ordinance",
        "prospectus",
        "rule",
        "regulation",
        "anti ragging",
        "refund",
        "discipline",
        "admission",
        "admission process",
        "selection process"
    ]

    website_keywords = [
        "latest",
        "latest notification",
        "notification",
        "notifications",
        "notice",
        "result",
        "results",
        "exam",
        "exam date",
        "datesheet",
        "date sheet",
        "circular",
        "circulars",
        "tender",
        "news",
        "official website",
        "website"
    ]

    # CLEAR WEBSITE QUERIES
    website_query_phrases = [
        "latest notification",
        "latest notifications",
        "current notification",
        "current notifications",
        "exam notification",
        "exam notifications",
        "latest exam notification",
        "latest exam notifications",
        "result notification",
        "result notifications",
        "latest result",
        "latest results",
        "current result",
        "current results",
        "official website",
        "university website",
        "university notifications",
        "university results",
        "admission notification",
        "admission notifications",
        "latest admission notification",
        "latest admission notifications",
        "current admission notification",
        "current admission notifications",
        "job notification",
        "job notifications",
        "latest job notification",
        "latest job notifications",
        "current job notification",
        "current job notifications",
        "employment notification",
        "employment notifications",
        "latest jobs",
        "latest job"
    ]

    if any(
        phrase in question
        for phrase in website_query_phrases
    ):
        return "website"
    
    # universityinfo
    university_keywords = [
        "university",
        "cluster university",
        "cus",
        "cus srinagar",
        "university mission",
        "university vision",
        "university name",
        "university established",
        "university type",
        "university headquarters",
        "university purpose",
        "university funding",

        "constituent colleges",
        "constituent college",

        "chancellor",
        "vice chancellor",
        "pro chancellor",
        "vc",
        "pro-chancellor",
        "registrar",

        "controller of examinations",
        "controller of examination",
        "controller of exams",
        "controller exams",
        "exam controller",
        "examination controller",
        "exam controller of university",
        "university exam controller",
        "university examination controller",
        "controller of university exams",
        "controller of university examinations"

]
    college_keywords = [
       "principal",
       "campus",
       "address",
       "location",
       "district",
       "state",

       "hostel",
       "library",
       "laboratory",
       "laboratories",
       "sports",
       "ncc",
       "nss",
       "facilities",
      #  "website",
       "google map",
       "email",
       
       "sri pratap college",
       "sp college",
       "spc",
       "amar singh college",
       "government college for women",
       "abdul ahad azad",
       "institute of advanced studies",
       "gcw",
       "asc",
       "aaamc",
       "aaamdc",
       "gdc bemina",
       "iase"   
    ]
    document_context = [
       "prospectus",
       "e-prospectus",
       "official document",
       "brochure",
       "handbook",
       "ordinance",
       "regulation",
       "policy",
       "circular",
       "notice"
    ]
    if any(x in question for x in document_context):
      return "pdf"
    programme_fields = [
      "fee",
      "fees",
      "eligibility",
      "duration",
      "intake",
    #   "admission",
      "selection",
      "overview"
    ]
    if any(x in question for x in programme_fields):
        return "programme"
    other_university_names = [
        "kashmir university",
        "ku",
        "uok",
        "university of kashmir",
        "cluster university jammu",
        "cluster university of jammu",
        "central university",
        "central university of kashmir",
        "cuk",
        "iust",
        "islamic university for science and technology",
        "nit",
        "national institute of technology",
        "nit srinagar",
        "skaust",
        "Sher-e-Kashmir University of Agricultural Sciences and Technology of Kashmir",
        "Sher e Kashmir University of Agricultural Sciences and Technology of Kashmir",
        "university of jammu",
        "central university jammu",
        "Baba Ghulam Shah Badhshah University",
        "bgsbu",
        "jammu university"
    ]
    if any(name in question for name in other_university_names):
        return "unknown_university"

    # uniinfo
    for word in university_keywords:
        if word in question:
            return "university"

    
    for word in college_keywords:
        if word in question:
            return "college"
    
    if "integrated" in question:
        return "programme"
    print("programme_keywords", programme_keywords)
        # GENERAL SUBJECT QUESTIONS
    subject_question_starts = [
        "what is ",
        "what are ",
        "tell me about ",
        "about ",
        "information about ",
        "information on "
    ]

    if any(
        question.startswith(phrase)
        for phrase in subject_question_starts
    ):
        return "programme"
    print("programme_keywords", programme_keywords)
  
    for word in programme_keywords:
        if word in question:
            return "programme"

    for word in pdf_keywords:
        if word in question:
            return "pdf"

    for word in website_keywords:
        if word in question:
            return "website"
        # spellcheck
    if (
        question.startswith("what is ")
        or question.startswith("what are ")
        or question.startswith("tell me about ")
        or question.startswith("about ")
        or question.startswith("information about ")
        or question.startswith("information on ")
    ):
        return "programme"

    return "knowledge"