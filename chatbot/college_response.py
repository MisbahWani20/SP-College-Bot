from college_search import search_college, get_last_college

def college_response(question):
    college = search_college(question)
    if college is None:
        college = get_last_college()
    if college is None:
        return None
    q = question.lower()
    answer = [f"🏛 <b>{college['college_name']}</b>\n"]
    if "principal" in q:
        answer.append(f"<b>Principal:</b> {college['principal']}")
    elif "google maps" in q or "google map" in q or "maps" in q or "map" in q:
        answer.append(
            f'📍<b>Google Maps:</b> '
            f'<a href="{college["google_maps"]}" target="_blank">'
            f'[View on Google Maps]</a>'
        )
    elif "address" in q or "location" in q or "located" in q:
        answer.append(f"<b>Address:</b> {college['address']}")

    elif "hostel" in q:
        answer.append(f"<b>Hostel:</b> {college['hostel']}")

    elif "library" in q:
        answer.append(f"<b>Library:</b> {college['library']}")

    elif "laboratory" in q or "laboratories" in q:
        answer.append(f"<b>Laboratories:</b> {college['laboratories']}")

    elif "sports" in q:
        answer.append(f"<b>Sports:</b> {college['sports']}")

    elif "ncc" in q:
        answer.append(f"<b>NCC:</b> {college['ncc']}")

    elif "nss" in q:
        answer.append(f"<b>NSS:</b> {college['nss']}")

    elif "department" in q or "departments" in q:
        answer.append(f"<b>Departments:</b> {college['departments']}")

    elif "programme" in q or "course" in q:
        answer.append(f"<b>Programmes Offered:</b> {college['programmes_offered']}")

    elif "website" in q:
        answer.append(
            f'🌐 <b>Website:</b> '
            f'<a href="{college["website"]}" target="_blank">'
            f'Visit Official Website</a>'
            )

    elif "email" in q:
        answer.append(
            f'📧 <b>Official Email:</b> '
            f'<a href="mailto:{college["official_email"]}">'
            f'{college["official_email"]}</a>'
            )

    elif "facility" in q or "facilities" in q:
        answer.append(f"<b>Facilities:</b> {college['facilities']}")
    elif "university" in q or "affiliated" in q:
        answer.append(
        f"<b>University:</b> {college['university']}"
    )
    elif "established" in q or "establishment" in q:
        answer.append(
        f"<b>Established:</b> {college['established']}"
    )
    elif "type" in q:
        answer.append(
        f"<b>Type:</b> {college['type']}"
    )
    elif "campus" in q:
        answer.append(
        f"<b>Campus:</b> {college['campus']}"
    )
    elif "district" in q:
        answer.append(
          f"<b>District:</b> {college['district']}"
    )
    elif "state" in q:
        answer.append(
          f"<b>State:</b> {college['state']}"
    )   

    else:
        return f"""🏛 <b>{college['college_name']}</b>

<b>Overview:</b> {college['overview']}

<b>Principal:</b> {college['principal']}

<b>Address:</b> {college['address']}

<b>Departments:</b> {college['departments']}

<b>Programmes Offered:</b> {college['programmes_offered']}

<b>Facilities:</b> {college['facilities']}

🌐 <b>Website:</b>
<a href="{college['website']}" target="_blank">Visit Official Website</a>

📧 <b>Email:</b>
<a href="mailto:{college['official_email']}">{college['official_email']}</a>

📍 <b>Google Maps:</b>
<a href="{college['google_maps']}" target="_blank">View Location</a>
"""
    return "\n\n".join(answer)