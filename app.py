import os
from flask import Flask, jsonify, render_template, request,send_from_directory 
from apscheduler.schedulers.background import BackgroundScheduler
from chatbot.intents import get_response
from chatbot.cus_website_data import (
    create_cus_website_table,
    fetch_notifications,
    fetch_results
)
from chatbot.translation import (
    translate_to_english,
    translate_from_english,
    normalize_translated_programme_names
)
from dotenv import load_dotenv
from admin import admin
from chatbot.knowledge_database import create_tables

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
print("Flask development server running")
app.register_blueprint(admin)
create_tables()
print("Database tables initialized.")
def update_cus_website_data():
    print("Updating CUS website data...")

    try:
        create_cus_website_table()

        notification_count = fetch_notifications()
        result_count = fetch_results()

        print(
            f"CUS website data updated successfully. "
            f"Notifications: {notification_count}, "
            f"Results: {result_count}"
        )

    except Exception as e:
        print("CUS website update failed:", e)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def chatbot_response():
    print("========== TRANSLATION ROUTE ==========")
    data = request.get_json()
    print(f"Request data: {data}")
    user_message = data["message"]
    language = data.get("language", "en")
    try:
        english_message = translate_to_english(
            user_message,
            language
          )
        english_message = normalize_translated_programme_names(
          english_message
        )
    except Exception as e:
        print("Translation input error:", e)

        translated_reply = (
            "Sorry, I’m unable to understand your request "
            "in this language right now. Please try again "
            "or use English."
        )

        print(f"Bot reply: {translated_reply}")

        return jsonify({
            "response": translated_reply
        })
        
    print("========== BEFORE CHATBOT ==========")
    print("Original question:", user_message) 
    print("English question:", english_message)
    try:
        bot_reply = get_response(english_message)
    except Exception as e:
        print("Chatbot processing error:", e)
        translated_reply = (
            "Sorry, I’m unable to process your request right now. "
            "Please try again."
        )

        print(f"Bot reply: {translated_reply}")

        return jsonify({
            "response": translated_reply
        })
    try:
        translated_reply = translate_from_english(
           bot_reply,
           language
          )

    except Exception as e:
        print("Translation output error:", e)
        translated_reply = (
            "Sorry, I’m unable to provide the response "
            "in the selected language right now. "
            "Please try again or use English."
           )
    print(f"Bot reply: {translated_reply}")
    return jsonify({
       "response": translated_reply
    })
 
@app.route("/prospectus")
def prospectus():
    pdf_directory = os.path.join(
        app.root_path,
        "data",
        "official_data",
        "pdfs"
    )

    return send_from_directory(
        pdf_directory,
        "Prospectus.pdf"
    )


if __name__ == "__main__":
    scheduler = None
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        print("CUS WEBSITE UPDATER STARTING")
        #Run once
        update_cus_website_data()

        scheduler = BackgroundScheduler()

        scheduler.add_job(
            update_cus_website_data,
            "interval",
            hours=6,
            id="cus_website_update",
            replace_existing=True
        )
        scheduler.start()
        print("CUS website updater started.")
        print("Next update will run after 6 hours.")
    try:
        app.run(
            debug=True,
            use_reloader=True
        )
    finally:
        if scheduler:
            scheduler.shutdown()
            print("CUS website updater stopped.")