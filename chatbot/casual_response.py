def get_casual_response(question):
    question = (question or "").lower().strip()

    if question in ["hi", "hello", "hey", "hii", "helo"]:
        return (
            "👋 Hello! How can I assist you with "
            "<b>Cluster University Srinagar</b>?"
        )

    if question in ["good morning", "good afternoon", "good evening"]:
        return (
            "👋 Hello! How can I assist you with "
            "<b>Cluster University Srinagar</b>?"
        )

    if question in ["thanks", "thank you", "thx"]:
        return (
            "You're welcome! 😊 "
            "Feel free to ask me anything about "
            "<b>Cluster University Srinagar</b>."
        )

    if question in ["bye", "goodbye", "good bye", "see you", "ok bye"]:
        return (
            "Goodbye! 👋 "
            "Feel free to return whenever you need information "
            "about <b>Cluster University Srinagar</b>."
        )

    if question in ["how are you", "how are you doing"]:
        return (
            "I'm doing well, thank you! 😊 "
            "I'm here to help you with information about "
            "<b>Cluster University Srinagar</b>."
        )
    return None