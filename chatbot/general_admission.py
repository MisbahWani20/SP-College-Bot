import re
CURRENT_ADMISSION_YEAR = "2026"
CURRENT_ADMISSION_SESSION = "2026–27"

OFFICIAL_WEBSITE = "https://www.cusrinagar.edu.in/"


ADMISSION_REGISTRATION_URL = (
    "https://www.cusrinagar.edu.in/Registration/Instructions/"
)

NEP_REGISTRATION_URL = (
    "https://www.cusrinagar.edu.in/NEP/Index"
)

PROVISIONAL_ADMISSION_FORM_URL = (
    "https://www.cusrinagar.edu.in/Entrance/ProvAdmForm"
)
ADMIT_CARD_URL = (
    "https://www.cusrinagar.edu.in/registration/admitcard"
)

NOTIFICATION_URL = (
    "https://www.cusrinagar.edu.in/Notification/NotificationListPartial"
)

UG_ADMISSION_URL = (
    "https://www.cusrinagar.edu.in/Registration/Instructions/"
    "notification/admissionnoticeforugprogrammes202627.pdf"
)
PROGRAMME_WORDS = {
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


def is_specific_programme_question(question):
    question = (question or "").lower().strip()
    words = set(
        re.findall(
            r"\b[a-z0-9]+\b",
            question
        )
    )

    if not words.intersection(PROGRAMME_WORDS):
        return False

    generic_words = {
        "what",
        "is",
        "the",
        "admission",
        "admissions",
        "process",
        "procedure",
        "how",
        "can",
        "i",
        "apply",
        "application",
        "for",
        "to",
        "get",
        "information",
        "about",
        "tell",
        "me",
        "please",
        "give",
        "details",
        "of",
        "programme",
        "program",
        "course",
        "courses",
        "ug",
        "pg",
        "undergraduate",
        "postgraduate",
        "it"
    }

    programme_words = words.intersection(
        PROGRAMME_WORDS
    )

    remaining_words = (
        words
        - generic_words
        - programme_words
    )

    return bool(remaining_words)

def get_general_admission_response(question):

    question = (question or "").lower().strip()
    # if is_specific_programme_question(question):
    #     return None

    # GENERAL ADMISSION PROCESS
    if any(word in question for word in [
        "admission process",
        "how to get admission",
        "how can i get admission",
        "how do i get admission",
        "how can i get admitted",
        "how to apply for admission",
        "how can i apply for admission",
        "how do i apply for admission",
        "admission procedure",
        "admission steps",
        "how do i apply"
    ]):

        return (
            "<b>🎓General Admission Process:</b><br><br>"
            "1. Check the eligibility criteria for the programme you "
            "want to apply for.<br>"
            "2. Read the relevant admission notification carefully.<br>"
            "3. Complete the online application form through the "
            "prescribed admission portal.<br>"
            "4. Enter your academic and personal details carefully.<br>"
            "5. Upload the required documents and photograph in the "
            "prescribed format.<br>"
            "6. Pay the applicable application fee online, where "
            "required.<br>"
            "7. Preview the application before final submission.<br>"
            "8. Submit the form and note your Form Number for future "
            "reference.<br>"
            "9. Follow the university notifications for entrance tests, "
            "merit lists, selection and document verification.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "🌐 UG / General Admission Registration</a><br>"
            f"<a href='{NEP_REGISTRATION_URL}' target='_blank'>"
            "🌐 PG Admission Registration</a>"
        )

    # ONLINE APPLICATION / PORTAL
    if any(word in question for word in [
        "admission portal",
        "application portal",
        "online admission",
        "online application",
        "where to apply",
        "where can i apply",
        "apply online",
        "admission website",
        "application website"
    ]):

        return (
            "<b>Online Admission:</b><br><br>"
            "Cluster University Srinagar conducts admissions through "
            "the online admission/registration system specified in "
            "the relevant admission notification.<br><br>"
            "Applicants should check the latest admission notification "
            "before applying because the application portal can differ "
            "for different programmes.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "CUS Admission Registration</a><br>"
            f"<a href='{OFFICIAL_WEBSITE}' target='_blank'>"
            "Official CUS Website</a>"
        )
    # DOCUMENTS
    if any(word in question for word in [
        "documents required",
        "required documents",
        "documents needed",
        "what documents",
        "documents for admission",
        "admission documents",
        "which documents"
    ]):

        return (
            "<b>📄 Documents for Admission:</b><br><br>"
            "The exact documents depend on the programme and admission "
            "notification. Applicants may be required to provide "
            "academic marks certificates, provisional/institution "
            "leaving certificate, character certificate, date-of-birth "
            "proof, migration certificate where applicable, and "
            "category/reservation certificate where applicable.<br><br>"
            f"For {CURRENT_ADMISSION_YEAR} registration, applicants should also keep a "
            "digital passport-size photograph ready. The CUS registration "
            "instructions specify an image size of 20–70 KB.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "🌐 UG / General Registration Instructions</a><br>"
            f"<a href='{NEP_REGISTRATION_URL}' target='_blank'>"
            "🌐 PG Registration Instructions</a>"
        )
    # PHOTOGRAPH / UPLOAD
    if any(word in question for word in [
        "photo",
        "photograph",
        "passport photo",
        "photo size",
        "photograph size",
        "upload photo"
    ]) and "admission" in question:

        return (
            "<b>Photograph Requirements:</b><br><br>"
            f"For Admission-{CURRENT_ADMISSION_YEAR} online registration, applicants should "
            "keep a digital passport-size photograph ready. The "
            "registration instructions specify JPG, BMP, JPEG or PNG "
            "format and a size between 20 KB and 70 KB.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "Official CUS Instructions</a>"
        )

    # APPLICATION FEE
    if any(word in question for word in [
        "application fee",
        "admission application fee",
        "form fee",
        "registration fee"
    ]):

        return (
            "<b>Application Fee:</b><br><br>"
            "Application fees are programme/admission specific. "
            "The applicable fee should be checked in the relevant "
            "admission notification before submission.<br><br>"
            f"For the general Admission-{CURRENT_ADMISSION_YEAR} registration instructions, "
            "CUS states that the application fee is to be paid online "
            "where applicable.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "Official CUS Admission Instructions</a>"
        )

    # UG ADMISSION
    if any(word in question for word in [
        "ug admission",
        "undergraduate admission",
        "under graduate admission",
        "bachelor admission",
        "ug admissions"
    ]):

        return (
            "<b>UG Admission:</b><br><br>"
            F"For the {CURRENT_ADMISSION_SESSION} academic session, admission to various "
            "Undergraduate programmes is notified through the prescribed "
            "admission process. Candidates should check the detailed "
            "eligibility conditions and programme/college information "
            "before applying.<br><br>"
            "For the UG admission notification issued by CUS, candidates "
            "were directed to apply online through the centralized "
            "Higher Education Department admission website.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "🌐 Official UG Registration & Instructions</a><br>"
            f"<a href='{UG_ADMISSION_URL}' target='_blank'>"
            "📄 Official UG Admission Notification</a><br>"
            f"<a href='{OFFICIAL_WEBSITE}' target='_blank'>"
            "🌐 CUS Official Website</a>"
        )

    # PG ADMISSION
    if any(word in question for word in [
        "pg admission",
        "postgraduate admission",
        "post graduate admission",
        "master admission",
        "pg admissions"
    ]):

        return (
            "<b>PG Admission:</b><br><br>"
            f"Cluster University Srinagar's {CURRENT_ADMISSION_SESSION} PG admission "
            "notifications cover 1-Year/2-Year Postgraduate and "
            "Integrated programmes through the prescribed university "
            "entrance/admission process.<br><br>"
            "Eligibility, programme details, entrance requirements, "
            "dates and selection information are programme-specific "
            "and should be checked in the latest PG admission "
            "notification.<br><br>"
            f"<a href='{NEP_REGISTRATION_URL}' target='_blank'>"
            "🌐Official PG Registration Portal</a><br>"
            f"<a href='{NOTIFICATION_URL}' target='_blank'>"
            "📢Latest CUS Admission Notifications</a>"
        )

    # CUET
    if any(word in question for word in [
        "cuet",
        "cuet ug",
        "common university entrance test"
    ]):

        return (
            "<b>CUET:</b><br><br>"
            "Cluster University Srinagar has issued admission "
            "notifications for specified Undergraduate programmes "
            "through CUET-UG conducted by the National Testing Agency "
            "(NTA).<br><br>"
            "CUET requirements are programme-specific, so applicants "
            "should check the relevant CUS admission notification for "
            "the programme they wish to apply for."
        )

    # ENTRANCE TEST
    if any(word in question for word in [
        "entrance test",
        "entrance exam",
        "entrance examination",
        "entrance requirement",
        "entrance requirements"
    ]):

        return (
            "<b>Entrance Test:</b><br><br>"
            "Some CUS programmes use an entrance-based admission "
            "process, while other admissions may be based on prescribed "
            "eligibility and/or academic merit. The exact procedure "
            "depends on the programme and current admission notification."
            "<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "CUS Admission Information</a>"
        )
        # GENERAL SELECTION PROCESS
    if any(phrase in question for phrase in [
        "how are students selected",
        "how are candidates selected",
        "how does selection work",
        "what is the selection process",
        "selection process",
        "how are admissions decided"
    ]):

        return (
            "<b>Selection Process:</b><br><br>"
            "Selection at Cluster University Srinagar depends on the "
            "programme and the applicable admission notification. "
            "Depending on the programme, selection may be based on "
            "eligibility, merit in the qualifying examination, an "
            "entrance test where applicable, seat availability and "
            "the applicable reservation rules.<br><br>"
            "Candidates should check the latest admission notification "
            "for the specific programme for the exact selection criteria."
            "<br><br>"
            f"<a href='{NOTIFICATION_URL}' target='_blank'>"
            "📢 Latest CUS Admission Notifications</a>"
        )


    # ADMIT CARD
    if any(word in question for word in [
        "admission admit card",
        "entrance admit card",
        "download admit card",
        "entrance hall ticket",
        "hall ticket"
    ]):

        return (
            "<b>Entrance Admit Card:</b><br><br>"
            "CUS provides an online facility for downloading "
            f"Entrance-{CURRENT_ADMISSION_YEAR} admit cards. Applicants are required to "
            "provide the requested registration/form information and "
            "date of birth.<br><br>"
            f"<a href='{ADMIT_CARD_URL}' target='_blank'>"
            "Download CUS Entrance Admit Card</a>"
        )
    # PROVISIONAL ADMISSION FORM
    if any(word in question for word in [
        "provisional admission form",
        "provisional form",
        "download admission form"
    ]):

        return (
            "<b>Provisional Admission Form:</b><br><br>"
            "CUS provides an online facility to download the "
            "Provisional Admission Form using the required "
            "registration/form or entrance information.<br><br>"
            f"<a href='{PROVISIONAL_ADMISSION_FORM_URL}' target='_blank'>"
            "Download Provisional Admission Form</a>"
        )

    # DOCUMENT VERIFICATION
    if any(word in question for word in [
        "document verification",
        "verification of documents",
        "verify documents",
        "documents verification"
    ]):

        return (
            "<b>Document Verification:</b><br><br>"
            "Selected/provisionally selected candidates may be required "
            "to report for verification of original documents and "
            "completion of admission formalities. Candidates should "
            "carry the documents specified in the relevant admission "
            "notification.<br><br>"
            "Admission remains subject to fulfilment of eligibility "
            "conditions and successful verification of documents."
        )

    # RESERVATION
    if any(word in question for word in [
        "reservation",
        "reserved category",
        "reservation policy",
        "category certificate"
    ]):

        return (
            "<b>Reservation:</b><br><br>"
            "Reservation provisions are applied according to the "
            "applicable Government of Jammu & Kashmir and university "
            "admission rules. Candidates claiming reservation should "
            "possess and submit the applicable category certificate "
            "within the prescribed requirements and deadline."
        )

    # ADMISSION GUIDELINES / INSTRUCTIONS
    if any(word in question for word in [
        "admission guidelines",
        "admission instructions",
        "registration instructions",
        "instructions for admission",
        "rules for admission"
    ]):

        return (
            "<b>Admission Instructions:</b><br><br>"
            "Applicants should check eligibility before applying, use "
            "a valid email ID and personal/guardian mobile number, "
            "carefully enter all required information, upload the "
            "prescribed documents and photograph, pay the applicable "
            "fee online, preview the form and finally submit it.<br><br>"
            "CUS states that changes are not allowed after successful "
            "final submission, so applicants should carefully verify "
            "their information before submitting the form.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "Official CUS Admission Instructions</a>"
        )

    # ADMISSION WEBSITE
    if (
        question in [
            "admission",
            "admissions",
            "general admission",
            "general admissions"
        ]
    ):

        return (
            "<b>Cluster University Srinagar Admissions</b><br><br>"
            "For admission information, applicants should check the "
            "official CUS website and the latest admission notification "
            "for their programme.<br><br>"
            f"<a href='{ADMISSION_REGISTRATION_URL}' target='_blank'>"
            "Admission Registration & Instructions</a><br>"
            f"<a href='{NOTIFICATION_URL}' target='_blank'>"
            "Latest Admission Notifications</a><br>"
            f"<a href='{OFFICIAL_WEBSITE}' target='_blank'>"
            "Official CUS Website</a>"
        )

    return None