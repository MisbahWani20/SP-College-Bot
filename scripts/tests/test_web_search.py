from chatbot.web_search import search_web_knowledge

while True:

    question = input("\nAsk: ").strip()

    if not question:
        continue

    result = search_web_knowledge(question)

    print("\n" + "=" * 60)

    if not result:
        print("No result found.")
        continue

    print("RESULT TYPE:", type(result))

    if isinstance(result, dict):

        print("TYPE:", result.get("type"))

        items = result.get("items", [])

        if not items:
            print("No items found.")
            continue

        for item in items:

            item_type, title, item_date, url = item

            print("\nTitle:", title)
            print("Date:", item_date)
            print("URL:", url)

    else:

        print("RAW RESULT:")
        print(result)

    print("=" * 60)