
class ConversationContext:

    def __init__(self):
        self.last_programme = None
        self.last_college = None
        self.last_subject = None
        self.last_query_type = None
        self.pending_clarification = None

    def update(
        self,
        query_type=None,
        programme=None,
        college=None,
        subject=None
    ):
        if query_type:
            self.last_query_type = query_type

        if programme:
            self.last_programme = programme

        if college:
            self.last_college = college

        if subject:
            self.last_subject = subject

    def set_pending_clarification(self, question, classification):
        self.pending_clarification = {
            "question": question,
            "classification": classification
        }

    def get_pending_clarification(self):
        return self.pending_clarification

    def clear_pending_clarification(self):
        self.pending_clarification = None

    def get_context(self):
        return {
            "last_programme": self.last_programme,
            "last_college": self.last_college,
            "last_subject": self.last_subject,
            "last_query_type": self.last_query_type
        }

    def has_follow_up_reference(self, question):
        question = question.lower().strip()

        follow_up_phrases = [
            "it",
            "its",
            "this",
            "that",
            "this programme",
            "that programme",
            "this course",
            "that course",
            "what about it",
            "what about this",
            "what about that",
            "and its",
            "and the"
        ]

        return any(
            phrase in question
            for phrase in follow_up_phrases
        )

    def clear(self):
        self.last_programme = None
        self.last_college = None
        self.last_subject = None
        self.last_query_type = None
        self.pending_clarification = None


conversation_context = ConversationContext()
