import re
from chatbot.programme_search import (
    search_programmes,
    get_last_programme,
    search_programme_list,
    search_subject_overview,
    search_all_matching_programmes,
    is_known_programme_question
)
from chatbot.conversation_context import conversation_context
from chatbot.general_admission import get_general_admission_response
from chatbot.spellcheck import find_closest_subject
from chatbot.query_intents import *
def programme_not_found_response():
    return (
        "I couldn't find a matching programme in my current database.<br><br>"
        "Please check the programme name and try again. "
        "You can also ask me about the programmes offered by "
        "<b>Cluster University Srinagar</b>."
    )

def programme_response(question):
    print("Programme Module Called")
    print("PROGRAMME RESPONSE QUESTION:", repr(question))

    question = question.lower().strip()
    question = re.sub(
        r"\big\b",
        "integrated",
        question
    )  
    context = conversation_context.get_context()
    last_programme = context.get("last_programme")

    explicit_programme_query = is_known_programme_question(question)
    print(
        "IS KNOWN PROGRAMME QUESTION RESULT:",
        explicit_programme_query
    )
    if not explicit_programme_query and not last_programme:
        general_admission_response = get_general_admission_response(question)
        if general_admission_response:
          return general_admission_response

    # FOLLOW-UP QUESTIONS
    programme_words = {
        "ba",
        "bsc",
        "bca",
        "bba",
        "bcom",
        "bed",
        "ma",
        "msc",
        "mca",
        "mba",
        "mcom",
        "med"
    }
    question_words = set(question.split())

    explicit_programme_query = is_known_programme_question(question)
    if (
        last_programme
        and not question_words.intersection(programme_words)
    ):
        explicit_programme_query = False
    
    print(
        "EXPLICIT PROGRAMME IN CURRENT QUESTION:",
        explicit_programme_query
    )
    explicit_programme = bool(
        question_words.intersection(programme_words)
    )
    follow_up_words = {
        "it",
        "its",
        "this",
        "that"
    }
    follow_up_reference = (
        (
            any(
                re.search(
                   rf"\b{re.escape(word)}\b",
                   question
                )
                #word in question.split()
                for word in follow_up_words
            ) 
            and not explicit_programme
        )
        or "this programme" in question
        or "this course" in question
        or "this degree" in question
        or "this program" in question
        or question.startswith("what about ")
        or question.startswith("how about ")
        or question.startswith("and ")
        or question in [
            "tell me more",
            "tell me more about it",
            "more information",
            "more about it",
            "more about this",
            "more about that",
            "about it",
            "about this",
            "about that"
        ]
        or (
            last_programme
            and not explicit_programme
            and (
                contains_any(question, FEE)
                or contains_any(question, DURATION)
                or contains_any(question, ELIGIBILITY)
                or contains_any(question, INTAKE)
                or contains_any(question, DEPARTMENT)
                or contains_any(question, ADMISSION)
                or contains_any(question, SELECTION)
                or contains_any(question, ENTRANCE)
            )
        )
    )

    if follow_up_reference and last_programme and not explicit_programme_query:
        print("FOLLOW-UP QUERY DETECTED")
        print("Previous programme:", last_programme)
        previous_programme = get_last_programme()
        if previous_programme:
            # programme_name = (
            #     f"{previous_programme['programme']}"
            #     f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}"
            # )
            # FEE
            if contains_any(question, FEE):
                return (
                    f"The fee for <b> {previous_programme['programme']}"
                    f"{' - ' + previous_programme ['specialization'] if previous_programme ['specialization'] else ''}</b> "
                    f"is:\n\n"
                    f"{previous_programme['fee']}"
                )
            # DURATION
            if contains_any(question, DURATION):
                return (
                    f"The <b>{previous_programme['programme']}"
                    f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
                    f"programme has a duration of "
                    f"<b>{previous_programme['duration']}</b>."
                )
            # ADMISSION
            if (
                contains_any(question, ADMISSION)
                or "get admitted" in question
            ):
                return (
                    f"For admission to <b>{previous_programme['programme']}"
                    f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b>:\n\n"
                    f"{previous_programme['admission_process']}"
                )
            # ELIGIBILITY
            if contains_any(question, ELIGIBILITY):
                return (
                    f"The eligibility requirements for "
                    f"<b>{previous_programme['programme']}"
                    f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
                    f"are:\n\n"
                    f"{previous_programme['eligibility']}"
                )
            # INTAKE
            if contains_any(question, INTAKE):
                return (
                    f"The intake for <b>{previous_programme['programme']}"
                    f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
                    f"is:\n\n"
                    f"{previous_programme['intake']}"
                )

            # DEPARTMENT
            if contains_any(question, DEPARTMENT):
                return (
                    f"<b>{previous_programme['programme']}"
                    f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
                    f"is offered under the following department:\n\n"
                    f"{previous_programme['department']}"
                )
            # ENTRANCE EXAM
            if contains_any(question, ENTRANCE):
                return (
                    f"Admission to <b>{previous_programme['programme']}"
                    f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
                    f"is based on the following process:\n\n"
                    f"{previous_programme['selection_process']}"
                )
            # SELECTION PROCESS
            if (
                contains_any(question, SELECTION)
                or "students selected" in question
            ):
                return (
                    f"The selection process for <b>{previous_programme['programme']}"
                    f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
                    f"is as follows:\n\n"
                  f"{previous_programme['selection_process']}"
                )

            # # FEE
            # if contains_any(question, FEE):
            #     return (
            #         f"📘 <b>{previous_programme['programme']}"
            #         f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b>\n\n"
            #         f"<b>Fee:</b> {previous_programme['fee']}"
            #     )

            # # DURATION
            # if contains_any(question, DURATION):
            #     return (
            #         f"📘 <b>{previous_programme['programme']}"
            #         f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b>\n\n"
            #         f"<b>Duration:</b> {previous_programme['duration']}"
            #     )

            # # ELIGIBILITY
            # if contains_any(question, ELIGIBILITY):
            #     return (
            #         f"📘 <b>{previous_programme['programme']}"
            #         f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b>\n\n"
            #         f"<b>Eligibility:</b> {previous_programme['eligibility']}"
            #     )

            # # INTAKE
            # if contains_any(question, INTAKE):
            #     return (
            #         f"📘 <b>{previous_programme['programme']}"
            #         f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b>\n\n"
            #         f"<b>Intake:</b> {previous_programme['intake']}"
            #     )

            # # DEPARTMENT
            # if contains_any(question, DEPARTMENT):
            #     return (
            #         f"📘 <b>{previous_programme['programme']}"
            #         f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b>\n\n"
            #         f"<b>Department:</b> {previous_programme['department']}"
            #     )       
            if (
                "tell me more" in question
                or "more information" in question
                or "more about" in question
                or question.strip() in [
                    "what about it",
                    "tell me about it",
                    "about it"
                ]
            ):
                programme_name = (
                   f"{previous_programme['programme']}"
                   f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}"
                )
                return (
                    f"Sure. Here is some more information about "
                    f"<b>{programme_name}</b>:\n\n"

                    f"<b>Programme Level:</b> "
                    f"{previous_programme['level']}\n\n"

                    f"<b>College:</b> "
                    f"{previous_programme['college']}\n\n"

                    f"<b>Department:</b> "
                    f"{previous_programme['department']}\n\n"

                    f"<b>Duration:</b> "
                    f"{previous_programme['duration']}\n\n"

                    f"<b>Eligibility:</b> "
                    f"{previous_programme['eligibility']}\n\n"

                    f"<b>Intake:</b> "
                    f"{previous_programme['intake']}\n\n"

                    f"<b>Fee:</b> "
                    f"{previous_programme['fee']}\n\n"

                    f"<b>Admission Process:</b> "
                    f"{previous_programme['admission_process']}\n\n"

                    f"<b>Selection Process:</b> "
                    f"{previous_programme['selection_process']}\n\n"

                    f"<b>Overview:</b> "
                    f"{previous_programme['subject_overview'] or previous_programme['overview']}"
                )
                
    college_query = (
        "which college" in question
        or "which colleges" in question
        or "what college" in question
        or "what colleges" in question
        or "colleges offering" in question
        or "colleges offer" in question
        or "colleges have" in question
        or "college has" in question
        or "where can i study" in question
        or "where to study" in question
        or "where can i do" in question
    )

    department_query = (
        "which department" in question
        or "what department" in question
        or "which dept" in question
        or "what dept" in question
        or "department offers" in question
        or "department offer" in question
        or "department for" in question
    )

    #NORMALIZE COMMON WORDING
    question = question.replace("programs", "programmes")
    question = question.replace("program", "programme")

    level_only_query = False

    level_patterns = [
        "pg programmes",
        "pg programme",
        "postgraduate programmes",
        "postgraduate programme",
        "post graduate programmes",
        "post graduate programme",

        "ug programmes",
        "ug programme",
        "undergraduate programmes",
        "undergraduate programme",
        "under graduate programmes",
        "under graduate programme",

        "integrated programmes",
        "integrated programme"
    ]

    if question in level_patterns:
        level_only_query = True

    if (
        ("pg" in question or "postgraduate" in question or "post graduate" in question)
        and "programme" in question
    ):
        level_only_query = True

    if (
        ("ug" in question or "undergraduate" in question or "under graduate" in question)
        and "programme" in question
    ):
        level_only_query = True

    if (
        "integrated" in question
        and "programme" in question
    ):
        level_only_query = True

    if level_only_query:
        programmes = search_programme_list(question)
        if not programmes:
            return "No matching programmes found."
        answer = (
            f"📚 <b>Available Programmes ({len(programmes)})</b>\n\n"
        )
        for p in programmes:
            programme_name = (
                p["programme"] or ""
            ).strip()
            specialization = (
                p["specialization"] or ""
            ).strip()
            college = (
                p["college"] or ""
            ).strip()
            line = f"📘 <b>{programme_name}"

            if specialization:
                line += f" - {specialization}"

            line += "</b>\n"

            if college:
                line += f"🏛 {college}\n"
            duration = (
                p["duration"] or ""
            ).strip()
            if duration:
                line += f"⏱ {duration}\n"
            line += "\n"

            answer += line

        return answer
    #COLLEGE QUESTIONS
    if college_query:

        matching_programmes = search_all_matching_programmes(
            question
        )

        print("\nMATCHING PROGRAMMES:")

        for p in matching_programmes:
            print(
                "PROGRAMME =", p["programme"],
                "| SPECIALIZATION =", p["specialization"],
                "| COLLEGE =", p["college"]
            )

        if not matching_programmes:
            return programme_not_found_response()

        colleges = []
        for p in matching_programmes:

            college = (
                p["college"] or ""
            ).strip()

            if college and college not in colleges:
                colleges.append(college)

        programme = matching_programmes[0]

        programme_name = (
            programme["programme"] or ""
        ).strip()

        specialization = (
            programme["specialization"] or ""
        ).strip()

        display_programme = programme_name

        if specialization and specialization.lower() not in [
            "general",
            "regular",
            "none"
        ]:
            display_programme += (
                f" - {specialization}"
            )

        answer = (
            f"<b>Colleges Offering "
            f"{display_programme}:</b>\n\n"
        )

        for college in colleges:
            answer += f"🏛 {college}\n"
        conversation_context.update(
            query_type="programme",
            programme=(
                f"{programme['programme']} "
                f"{programme['specialization'] or ''}"
            ).strip(),
            college=programme["college"],
            subject=programme["specialization"]
        )
        print(
            "CONTEXT UPDATED:",
            conversation_context.get_context()
        )

        return answer

    list_keywords = [
        "list",
        "show",
        "display",
        "available",
        "offered",
        "offer",
        "offers",
        "programmes offered",
        "courses offered",
        "provides",
        "provide",
        "programmes provided",
        "courses provided",
        "all programmes",
        "all programs",
        "available in",
        "programmes",
        "programme",
        "programs",
        "program"
    ]
 
    is_list_query = (
        any(word in question for word in list_keywords)
        and not college_query
        and not department_query
    )

    if is_list_query:
        programmes = search_programme_list(
            question
        )
        if not programmes:
            return programme_not_found_response()

        answer = (
            f"📚 <b>Available Programmes "
            f"({len(programmes)})</b>\n\n"
        )

        for p in programmes:
            programme_name = (
                p["programme"] or ""
            ).strip()

            specialization = (
                p["specialization"] or ""
            ).strip()

            college = (
                p["college"] or ""
            ).strip()

            line = (
                f"📘 <b>{programme_name}"
            )

            if specialization:
                line += (
                    f" - {specialization}"
                )

            line += "</b>\n"

            if college:
                line += (
                    f"🏛 {college}\n"
                )
                duration = (
                    p["duration"] or ""
                ).strip()
                if duration:
                    line += f"⏱ {duration}\n"
                line += "\n"
            answer += line
        return answer

    level_words = {
        "bsc", "msc", "ba", "ma", "bca", "mca",
        "bba", "mba", "bcom", "mcom",
        "bed", "med", "integrated"
    }
    question_words = set(question.split())

    specific_programme_query = any(
        word in question_words
        for word in level_words
    )
    generic_subject_query = (
        question.startswith("what is ")
        or question.startswith("what are ")
        or question.startswith("information on ")
        or question.startswith( "tell me about")
        or question.startswith("about") 
        or question.startswith("information about")
    )

    if generic_subject_query and not specific_programme_query:
        subject_query = question
        subject_query = re.sub(
           r"^(what is|what are|information on|tell me about|information about|about)\s+",
           "",
            subject_query
        ).strip()

        #spellcheck
        print(
            "GENERAL SUBJECT QUERY:",
            subject_query
        )
        print(
            "SUBJECT OVERVIEW SEARCH:",
            repr(subject_query)
        )
      
        subject_result = search_subject_overview(
            subject_query
        )

        #spellcheck
        if subject_result is None:

            matched_subject, _ = find_closest_subject(
                    subject_query,
                    # threshold=0.70
                )
        
            if matched_subject:

                subject_result = search_subject_overview(
                    matched_subject
                )
            #yehan tak

        if subject_result:
         return (
            f"📘 <b>{subject_result['subject'].title()}</b>\n\n"
            f"{subject_result['overview']}"
         )
        

    if department_query and question.startswith("department for "):
        programme_search_question = question.replace(
         "department for ",
         "tell me about ",
         1
        )
    else:
        programme_search_question = question
    
    programme = search_programmes(
        programme_search_question
    )
    if programme is None:
        return programme_not_found_response()
    # if programme is None:
    #     context = conversation_context.get_context()
    #     last_programme = context.get("last_programme")

    # if last_programme and explicit_programme_query:

    #     previous_programme = get_last_programme()

    #     if previous_programme:

    #         if contains_any(question, FEE):
    #             return (
    #                 f"The fee for <b>{previous_programme['programme']}"
    #                 f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
    #                 f"is:\n\n"
    #                 f"{previous_programme['fee']}"
    #             )

    #         if contains_any(question, DURATION):
    #             return (
    #                 f"The <b>{previous_programme['programme']}"
    #                 f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
    #                 f"programme has a duration of "
    #                 f"<b>{previous_programme['duration']}</b>."
    #             )

    #         if contains_any(question, ELIGIBILITY):
    #             return (
    #                 f"The eligibility requirements for "
    #                 f"<b>{previous_programme['programme']}"
    #                 f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
    #                 f"are:\n\n"
    #                 f"{previous_programme['eligibility']}"
    #             )

    #         if contains_any(question, INTAKE):
    #             return (
    #                 f"The intake for <b>{previous_programme['programme']}"
    #                 f"{' - ' + previous_programme['specialization'] if previous_programme['specialization'] else ''}</b> "
    #                 f"is:\n\n"
    #                 f"{previous_programme['intake']}"
    #             )
    #     return programme_not_found_response()
    
    conversation_context.update(
        query_type="programme",
        programme=(
          f"{programme['programme']} "
          f"{programme['specialization'] or ''}"
        ).strip(),
        college=programme["college"],
        subject=programme["specialization"]
    )
    print(
       "CONTEXT UPDATED:",
       conversation_context.get_context()
    )

    # DEPARTMENT QUERY
    if department_query:
        return (
          f"📘 <b>{programme['programme']}"
          f"{' - ' + programme['specialization'] if programme['specialization'] else ''}</b>\n\n"
          f"<b>Department:</b> {programme['department']}"
        )

    #SINGLE PROGRAMME RESPONSE
    response = [
        f"📘 <b>{programme['programme']}"
    ]

    if programme["specialization"]:
        response[0] += (
            f" - {programme['specialization']}"
        )

    response[0] += "</b>\n"
    if contains_any(question, INTAKE):
        response.append(
            f"<b>Intake:</b> "
            f"{programme['intake']}"
        )

    if contains_any(question, ELIGIBILITY):
        response.append(
            f"<b>Eligibility:</b> "
            f"{programme['eligibility']}"
        )

    if contains_any(question, FEE):
        response.append(
            f"<b>Fee:</b> "
            f"{programme['fee']}"
        )

    if contains_any(question, DURATION):
        response.append(
            f"<b>Duration:</b> "
            f"{programme['duration']}"
        )
    
    if contains_any(question, DEPARTMENT):
        response.append(
            f"<b>Department:</b> "
            f"{programme['department']}"
        )

    if contains_any(question, ADMISSION):
        response.append(
            f"<b>Admission Process:</b> "
            f"{programme['admission_process']}"
        )

    if contains_any(question, SELECTION):
        response.append(
            f"<b>Selection Process:</b> "
            f"{programme['selection_process']}"
        )
    if len(response) > 1:
        return "\n\n".join(response)

    return f"""📘{programme['programme']}{"-" + programme['specialization'] if programme['specialization'] else ""}

<b>Programme Level</b>: {programme['level']}

<b>College</b>: {programme['college']}

<b>Department</b>: {programme['department']}

<b>Duration</b>: {programme['duration']}

<b>Eligibility</b>: {programme['eligibility']}

<b>Intake</b>: {programme['intake']}

<b>Fee</b>: {programme['fee']}

<b>Admission Process</b>: {programme['admission_process']}

<b>Selection Process</b>: {programme['selection_process']}

<b>Overview</b>: {programme['subject_overview'] or programme['overview']}

<b>School</b>: {programme['school']}

<b>Campus</b>: {programme['campus']}
"""