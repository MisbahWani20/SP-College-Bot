import json
import re
from chatbot.groq_service import ask_groq
from chatbot.gemini_service import ask_gemini
def ask_llm(question):
    """
    Ask the primary LLM (Groq).
    If Groq fails, use Gemini as backup.
    """
    if not question:
        return None
    print("\n===== LLM SERVICE =====")
    print("Question:", question)
    # PRIMARY: GROQ
    print("Trying Groq...")
    try:
       groq_answer = ask_groq(question)
    except Exception as error:
        print ("Groq error:", error)
        groq_answer =None
    if groq_answer:
        print("Groq response received.")
        return groq_answer
    print("Groq failed or returned no answer.")
    # BACKUP: GEMINI
    print("Trying Gemini backup...")
    try:
        gemini_answer = ask_gemini(question)
    except Exception as error:
            print ("Gemini error:", error)
            gemini_answer = None

    if gemini_answer:
        print("Gemini response received.")
        return gemini_answer

    print("Both Groq and Gemini failed.")

    return None


def classify_with_llm(question):
    """
    Understand the user's natural-language question.
    The LLM does NOT answer the question.
    It only determines:
        intent
        entity
        question_type
        level
    Groq is primary.
    Gemini is fallback.
    If both fail, None is returned and the existing
    CUS query router can take over.
    """
    if not question:
        return None

    prompt = f"""
You are the language-understanding and intent-classification
component of a chatbot STRICTLY dedicated to Cluster University
Srinagar (CUS).

Your job is ONLY to understand the user's question.

DO NOT answer the user.

DO NOT provide explanations.

DO NOT invent information.

The chatbot must remain strictly within the scope of
Cluster University Srinagar.

============================================================
ALLOWED INTENTS
============================================================

1. programme

Use "programme" when the user is asking about a programme,
course, subject offered as a CUS programme, specialization,
programme fee, duration, eligibility, intake, department,
college offering the programme, admission process or selection
process for a SPECIFIC programme.

Natural variations must be understood.

Examples:

"What is BSc IT?"
"Tell me about BSc IT"
"How much does BSc IT cost?"
"BSc IT fees?"
"How long is BSc IT?"
"Where is BSc IT offered?"
"Can I get admission in BSc IT?"
"What is required for BSc IT admission?"

All -> programme


IMPORTANT:

A subject or technical concept alone is NOT automatically a
CUS programme.

"What is machine learning?"
"What is quantum computing?"
"Explain artificial intelligence."

These are NOT programme questions unless the user clearly
connects them to a CUS programme.

Examples:

"What is MSc Artificial Intelligence and Machine Learning?"
"Tell me about the AI and ML programme at CUS."
"Does CUS offer a programme in data science?"

-> programme


2. college

Use "college" when the user asks about a specific constituent
college of Cluster University Srinagar.

Examples:

"Tell me about Amar Singh College."
"Who is the principal of Islamia College?"
"What facilities are available at SP College?"
"Where is Government Degree College Bemina?"

-> college


3. university

Use "university" when the question concerns Cluster University
Srinagar itself.

Examples:

"Who is the Vice Chancellor?"
"Who is the registrar?"
"When was Cluster University Srinagar established?"
"What is the mission of CUS?"
"Tell me about Cluster University Srinagar."

-> university


4. admission

Use "admission" ONLY for GENERAL CUS admission questions
that do not refer to a specific programme.

Examples:

"How can I apply?"
"How do I apply for admission?"
"What documents do I need?"
"When does admission start?"
"When will admissions open?"
"What is the application fee?"
"Where is the admission portal?"
"What are the admission guidelines?"

If a specific programme is mentioned, use "programme".

Example:

"What is the admission process for BSc IT?"

-> programme


5. pdf

Use "pdf" when the user explicitly asks about an official
CUS document or PDF.

Examples:

"Show me the prospectus."
"Give me the admission brochure."
"What does the ordinance say?"
"Tell me what is on page 20 of the prospectus."
"Show the regulations."

-> pdf


6. website

Use "website" for current/latest information obtained from
the official CUS website.

Examples:

"What are the latest notifications?"
"Any new exam notices?"
"Show the latest results."
"Are there any new admission notifications?"
"Any recent job notifications?"

-> website


7. general_ai

Use "general_ai" when the question is general educational,
scientific, technical or everyday knowledge and is NOT
specifically about Cluster University Srinagar.

Examples:

"What is machine learning?"
"Explain blockchain."
"What is quantum computing?"
"How does cloud computing work?"

IMPORTANT:
The chatbot is STRICTLY a Cluster University Srinagar
assistant.

The chatbot must NOT answer these questions as general
knowledge.

They are classified as general_ai so the application can
politely keep the conversation within CUS scope.


8. sp_college_affiliation

Use "sp_college_affiliation" when the user asks which
university Sri Pratap College (SP College) is affiliated
with, regardless of the wording or spelling mistakes.

Examples:
- "With which university is SP College affiliated?"
- "Which university is SP College under?"
- "Who is SP College affiliated to?"
- "Does Sri Pratap College come under CUS?"
- "SP College belongs to which university?"
- "Is SP College affiliated with Cluster University Srinagar?"

For these questions, return:
intent = "sp_college_affiliation"
entity = "Sri Pratap College"
question_type = "affiliation inquiry"
level = "unknown"

Do not use this intent for general questions about
Cluster University Srinagar.

9. unknown

Use "unknown" when the question cannot confidently be
classified into the above categories.


10. unknown

Use "unknown" when the question cannot confidently be
classified into the above categories.

============================================================
CUS SCOPE
============================================================

If the user asks about another university, institution,
college system or unrelated organization, do NOT treat it as
CUS information.

Examples:

"What is Kashmir University?"
"What is IUST?"
"Tell me about NIT Srinagar."
"What courses does University of Jammu offer?"

-> unknown

The application will respond that it is specifically for
Cluster University Srinagar.

============================================================
ENTITY
============================================================

The entity should contain the main subject.
IMPORTANT PROGRAMME NAME NORMALIZATION:

"BEd", "B.Ed", "B Ed", "B. Ed", and "Bachelor of Education"
all refer to the same programme: B.Ed.

When the user clearly refers to BEd/B.Ed as a programme,
classify it as:

intent = programme
entity = "B.Ed"

Do NOT classify "BEd" or "B.Ed" as general_ai.

For the regular B.Ed programme, the level is "ug".

Examples:

"What is BEd?"
"What is B.Ed?"
"Tell me about BEd"
"Tell me about B.Ed"
"How long is BEd?"
"Which college offers B.Ed?"
"Which college offers BEd?"

All refer to the B.Ed programme.

Examples:

"What is BSc IT?"
entity = "BSc IT"

"How much does BSc IT cost?"
entity = "BSc IT"

"What is the admission process?"
entity = "admission"

"Tell me about Amar Singh College."
entity = "Amar Singh College"

"What is machine learning?"
entity = "machine learning"





QUESTION TYPE

Use a short meaningful description such as:
definition
fee inquiry
eligibility inquiry
duration inquiry
intake inquiry
admission procedure
selection process
programme discovery
college information
university information
latest notifications
result inquiry
document inquiry
department inquiry
college inquiry

IMPORTANT DISTINCTION BETWEEN DEPARTMENT INQUIRY AND COLLEGE INQUIRY:

Use "department inquiry" when the user is asking which
academic department a specific programme belongs to or which
department offers the programme.

Examples:

"Which department offers BSc IT?"
"BSc IT comes under which department?"
"What department is BSc IT under?"
"Which department is BSc IT offered under?"

All -> question_type = "department inquiry"


Use "college inquiry" when the user is asking which college
offers, provides, or has a specific programme.

Examples:

"Which college offers BSc IT?"
"Where is BSc IT offered?"
"Where can I study BSc IT?"
"Which colleges offer BSc IT?"
"What college has BSc IT?"
"Which college provides BSc IT?"

All -> question_type = "college inquiry"


IMPORTANT:
The word "where" in a programme question usually refers to
the college/location where the programme is offered, NOT the
academic department.
For example:
"Where is BSc IT offered?"
-> question_type = "college inquiry"
"Which department offers BSc IT?"
-> question_type = "department inquiry"


CLARIFICATION AND INCOMPLETE QUESTIONS

Determine whether the user's question contains enough information
to answer correctly.

Return these additional fields:

"needs_clarification": true or false
"clarification_question": a short, professional question, or ""

Use needs_clarification = true when essential information is
missing and cannot be determined from the user's message.

Examples:

1. User: "programmes offered by CUS"

intent = "programme"
entity = ""
question_type = "programme discovery"
level = "unknown"
needs_clarification = true

clarification_question should ask whether the user wants
UG, PG, Integrated, or all programmes.

2. User: "eligibility"

intent = "programme"
entity = ""
question_type = "eligibility inquiry"
level = "unknown"
needs_clarification = true

Ask which programme the user wants eligibility information for.

3. User: "duration"

intent = "programme"
entity = ""
question_type = "duration inquiry"
level = "unknown"
needs_clarification = true

Ask which programme the user wants to know about.

4. User: "PG programmes"

intent = "programme"
entity = ""
question_type = "programme discovery"
level = "pg"
needs_clarification = false

5. User: "all programmes offered by CUS"

intent = "programme"
entity = ""
question_type = "programme discovery"
level = "unknown"
needs_clarification = false

The user has explicitly requested all programmes, so do not
ask them to choose a category.

6. User: "What is B.Ed?"

intent = "programme"
entity = "B.Ed"
question_type = "definition"
level = "ug"
needs_clarification = false

IMPORTANT:

- Understand meaning, not just exact phrases.
- Do not ask for information the user has already provided.
- Do not treat "CUS" as the name of a specific programme.
- Do not ask unnecessary clarification questions when the
  requested information can be retrieved.
- For a single attribute such as fee, duration, eligibility,
  intake, admission, or selection, identify the missing
  programme if no programme is specified.
- When a programme is explicitly named, preserve its identity.
- Never invent programme names or university facts.
- If the question is already sufficiently clear, set
  needs_clarification = false and clarification_question = "".


LEVEL

Use ONLY:
"ug"
"pg"
"integrated"
"unknown"

Use "unknown" if the level is not clear.

Examples:

"BSc IT" -> ug
"MSc IT" -> pg
"Integrated BSc BEd" -> integrated


VERY IMPORTANT

Understand meaning rather than exact wording.

For example, these all mean fee inquiry:

"How much is BSc IT?"
"What does BSc IT cost?"
"How much will BSc IT cost me?"
"What are the charges for BSc IT?"
"Tell me the fee for BSc IT."
"BSc IT fee?"

They should all produce:

intent = programme
entity = BSc IT
question_type = fee inquiry

Likewise:

"How long does it take?"
"What's the duration?"
"How many years is it?"
"How many years does this course take?"

When referring to a previously discussed programme,
understand that it is a follow-up question.


Return ONLY valid JSON.

No markdown.
No code fences.
No explanation.

Return ONLY valid JSON.

Return exactly these six fields:

{{
    "intent": "...",
    "entity": "...",
    "question_type": "...",
    "level": "...",
    "needs_clarification": false,
    "clarification_question": ""
}}

USER QUESTION:
{question}
"""
    # PRIMARY: GROQ
    print("\n===== LLM CLASSIFICATION =====")
    print("Trying Groq classifier...")
    groq_result = None
    try:
        groq_result = ask_groq(prompt)
    except Exception as error:
        print("Groq classifier error:", error)

    if groq_result:
        classification = parse_classification(
            groq_result
        )

        if classification:
            print(
                "Groq classification successful."
            )
            return classification

        print(
            "Groq returned invalid classification."
        )

    else:
        print(
            "Groq classifier failed."
        )
    # BACKUP: GEMINI
    print(
        "Trying Gemini classifier backup..."
    )
    try:
        gemini_result = ask_gemini(prompt)
    except Exception as error:
        print("Gemini classifier error:", error)
        gemini_result= None

    if gemini_result:
        classification = parse_classification(
            gemini_result
        )

        if classification:
            print(
                "Gemini classification successful."
            )
            return classification

        print(
            "Gemini returned invalid classification."
        )

    else:
        print(
            "Gemini classifier failed."
        )

    print(
        "Both Groq and Gemini classification failed."
    )

    return None


def parse_classification(result):
    """
    Safely extract classification JSON from an LLM response.

    Handles:
        normal JSON
        markdown fences
        accidental surrounding text
        malformed output

    Never raises an exception to the chatbot.

    """
    if not result:
        return None

    try:
        result = result.strip()
        # Remove accidental markdown fences
        result = re.sub(
            r"```(?:json)?",
            "",
            result,
            flags=re.IGNORECASE
        )
        result = result.replace("```", "").strip()
        try:
            classification = json.loads(result)
        except json.JSONDecodeError:
            match = re.search(
                r"\{.*\}",
                result,
                flags=re.DOTALL
            )
            if not match:
                print("No JSON object found in LLM response.")
                print("Raw response:", result)
                return None
            classification = json.loads(
                match.group(0)
            )
        if not isinstance(classification, dict):
            print("Classification is not a dictionary.")
            return None
        # Make sure the expected fields exist
        required_fields = {
            "intent",
            "entity",
            "question_type",
            "level",
            "needs_clarification",
            "clarification_question"
        }

        if not required_fields.issubset(
            classification.keys()
        ):
            print(
                "Classification missing required fields:",
                classification
            )
            return None
        classification["intent"] = str(
            classification["intent"]
        ).strip().lower()

        classification["entity"] = str(
            classification["entity"]
        ).strip()

        classification["question_type"] = str(
            classification["question_type"]
        ).strip().lower()
        classification["question_type"] = (
            classification["question_type"]
            .replace("documentinquiry", "document inquiry")
        )

        classification["level"] = str(
            classification["level"]
        ).strip().lower()
        
        if not isinstance(
            classification["needs_clarification"],
            bool
        ):
            print("Invalid needs_clarification value.")
            return None

        classification["clarification_question"] = str(
           classification["clarification_question"] or ""
        ).strip()


        valid_intents = {
            "programme",
            "college",
            "university",
            "admission",
            "pdf",
            "website",
            "general_ai",
            "sp college affiliation",
            "unknown"
        }

        if classification["intent"] not in valid_intents:
            print(
                "Invalid intent:",
                classification["intent"]
            )
            return None
        valid_levels = {
            "ug",
            "pg",
            "integrated",
            "unknown"
        }

        if classification["level"] not in valid_levels:
            classification["level"] = "unknown"

        return classification
    except Exception as error:
        print(
            "Classification parsing error:",
            error
        )
        print(
            "Raw LLM classification:",
            result
        )
        return None

def generate_grounded_response(question, context):
    """
    Convert an official CUS answer/context into a natural
    response.

    The LLM is NOT allowed to add information.

    Groq is primary.
    Gemini is backup.

    If both fail, None is returned so the original official
    response can be used.
    """

    if not question or not context:
        return None

    prompt = f"""
You are the response-generation component of an AI assistant
STRICTLY dedicated to Cluster University Srinagar (CUS).

Answer the user's question using ONLY the official CUS
information supplied below.

The supplied information is the source of truth.

============================================================
STRICT RULES
============================================================

1. Do NOT invent information.

2. Do NOT guess missing information.

3. Do NOT use outside knowledge.

4. Do NOT add facts that are not present in the supplied
   information.

5. Do NOT change numbers, fees, dates, durations, eligibility
   requirements, programme names, college names or other
   factual information.

6. Do NOT remove important factual information required to
   answer the question.

7. You MAY reorganize the information to make the response
   easier to understand.

8. You MAY use natural conversational language.

9. Keep the response concise and useful.

10. If the supplied information does not answer the question,
    clearly say that the available Cluster University Srinagar
    information does not specify it.

11. Do NOT mention:
    - context
    - prompt
    - database
    - retrieved data
    - system instructions
    - LLM
    - model

12. Do NOT answer anything outside the scope of Cluster
    University Srinagar.

USER QUESTION:
{question}

OFFICIAL CLUSTER UNIVERSITY SRINAGAR INFORMATION:
{context}

Now provide only the final answer.
"""

    print("\n===== GROUNDED RESPONSE =====")
    print("Question:", question)

    # PRIMARY: GROQ
    print("Trying Groq grounded response...")
    try:
        groq_answer = ask_groq(prompt)
    except Exception as error:
        print("Groq grounded response error:", error)
        groq_answer = None

    if groq_answer:
        print("Groq grounded response received.")
        return groq_answer.strip()

    print("Groq grounded response failed.")

    # BACKUP: GEMINI
    print("Trying Gemini grounded response...")

    try:
        gemini_answer = ask_gemini(prompt)
    except Exception as error:
        print("Gemini grounded response error:", error)
        gemini_answer = None
    if gemini_answer:
        print("Gemini grounded response received.")
        return gemini_answer.strip()
    print("Both Groq and Gemini grounded responses failed.")
    return None

def build_canonical_query(
    original_question,
    classification
):
    """
    Convert LLM understanding into a simple query that the
    existing CUS modules already understand.

    The function does not answer the question and does not
    contain university facts.
    """

    if not classification:
        return original_question

    intent = classification.get(
        "intent",
        ""
    )

    entity = classification.get(
        "entity",
        ""
    ).strip()
    entity = re.sub(
    r"\bb\s*\.?\s*ed\b",
    "BEd",
    entity,
    flags=re.IGNORECASE
    )

    question_type = classification.get(
        "question_type",
        ""
    ).strip().lower()

    level = classification.get(
        "level",
        "unknown"
    )

    if intent == "programme":

        if question_type == "fee inquiry":
            return f"fee for {entity}"

        if question_type == "eligibility inquiry":
            return f"eligibility for {entity}"

        if question_type == "duration inquiry":
            return f"duration of {entity}"

        if question_type == "intake inquiry":
            return f"intake for {entity}"

        if question_type == "admission procedure":
            return f"admission process for {entity}"

        if question_type == "selection process":
            return f"selection process for {entity}"

        if question_type == "department inquiry":
            return f"department for {entity}"

        if question_type == "college inquiry":
            return f"which colleges offer {entity}"

        if question_type == "programme discovery":
            if entity:
                return f"which colleges offer {entity}"
            if level in {
                "ug",
                "pg",
                "integrated"
            }:
                return (
                    f"list all {level} programmes"
                )
        if entity:
            return f"tell me about {entity}"
    if intent == "college":
        if entity:
            return f"tell me about {entity}"
    if intent == "university":
        return original_question
    if intent == "admission":
        return original_question
    return original_question


def classify_sp_college_question(question):
    """
    Classify questions specifically for Sri Pratap College.
    Uses the existing Groq/Gemini providers through ask_groq and ask_gemini.
    Returns structured JSON or None if classification fails.
    """

    prompt = f"""
You are a query classifier for Sri Pratap College, Srinagar.

Classify the user's question. Do not answer the question.
Return ONLY valid JSON with these keys:
- intent
- entity
- question_type
- level

Allowed intents:
college_info, programme, principal, department, admission,
syllabus, announcement, contact, facilities, unknown

For level, use:
ug, pg, integrated, unknown

Rules:
- Understand common abbreviations such as BSc IT, MSc IT, UG IT and PG IT.
- Do not invent programme names or details.
- If the question is about a programme's eligibility, fee, duration,
  intake, subjects, or admission process, use intent "programme".
- If the question is about the principal, use intent "principal".
- If it asks about phone, email, address, website, or map, use intent "contact".
- If the question is unrelated to Sri Pratap College, use intent "unknown".
- The entity should contain the relevant programme, person, or topic.
- question_type should describe the requested detail in a few words.

Question: {question}

JSON:
"""

    for provider in (ask_groq, ask_gemini):
        try:
            response = provider(prompt)

            if not response:
                continue

            # Support providers that return plain text.
            if isinstance(response, dict):
                result = response
            else:
                text = str(response).strip()
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)

                start = text.find("{")
                end = text.rfind("}")

                if start == -1 or end == -1:
                    continue

                result = json.loads(text[start:end + 1])

            allowed_intents = {
                "college_info", "programme", "principal", "department",
                "admission", "syllabus", "announcement", "contact",
                "facilities", "unknown"
            }
            intent = str(result.get("intent", "unknown")).lower().strip()
            if intent not in allowed_intents:
                continue
            return {
                "intent": intent,
                "entity": str(result.get("entity", "")).strip(),
                "question_type": str(
                    result.get("question_type", "")
                ).strip(),
                "level": str(result.get("level", "unknown")).lower().strip()
            }
        except Exception as exc:
            print(f"SP College classification failed: {exc}")
    return None


