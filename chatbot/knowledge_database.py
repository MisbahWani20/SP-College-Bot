import sqlite3
DATABASE_NAME = "chatbot/knowledge.db"
def get_connection():
    return sqlite3.connect(DATABASE_NAME)
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_topics(
            topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_fields(
            field_id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            FOREIGN KEY(topic_id) REFERENCES knowledge_topics(topic_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_values(
            value_id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id INTEGER NOT NULL,
            field_value TEXT NOT NULL,
            source TEXT,
            url TEXT,
            last_updated TEXT,
            FOREIGN KEY(field_id) REFERENCES knowledge_fields(field_id)
        )
    """)

  
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications(
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            summary TEXT,
            publish_date TEXT,
            url TEXT
        )
    """)

   
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history(
            chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT,
            bot_response TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_programmes (

           id INTEGER PRIMARY KEY AUTOINCREMENT,
           programme TEXT NOT NULL,
           specialization TEXT,
           level TEXT,
           college TEXT,
           department TEXT,
           duration TEXT,
           programme_type TEXT,
           school TEXT,
           campus TEXT,
           eligibility TEXT,
           intake TEXT,
           fee TEXT,
           admission_process TEXT,
           selection_process TEXT,
           overview TEXT,
           subject_overview TEXT,
           source TEXT,
           url TEXT,
           last_updated TEXT
       )
    """)
    cursor.execute("""

        CREATE TABLE IF NOT EXISTS college_master (
           college_id INTEGER PRIMARY KEY AUTOINCREMENT,
           college_name TEXT NOT NULL,
           short_name TEXT,
           university TEXT,
           established TEXT,
           type TEXT,
           campus TEXT,
           address TEXT,
           district TEXT,
           state TEXT,
           principal TEXT,
           overview TEXT,
           departments TEXT,
           programmes_offered TEXT,
           library TEXT,
           hostel TEXT,
           laboratories TEXT,
           sports TEXT,
           ncc TEXT,
           nss TEXT,
           facilities TEXT,
           website TEXT,
           google_maps TEXT,
           official_email TEXT
           )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS university_info (
           university_info_id INTEGER PRIMARY KEY AUTOINCREMENT,
           intent TEXT,
           topic TEXT,
           field TEXT,
           value TEXT,
           source TEXT,
           url TEXT,
           email TEXT
           )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT,
            department TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            office TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    

def add_topic(topic_name, category, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO knowledge_topics (topic_name, category, description)
        VALUES (?, ?, ?)
    """, (topic_name, category, description))

    conn.commit()
    topic_id = cursor.lastrowid
    conn.close()

    return topic_id


def add_field(topic_id, field_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO knowledge_fields (topic_id, field_name)
        VALUES (?, ?)
    """, (topic_id, field_name))

    conn.commit()
    field_id = cursor.lastrowid
    conn.close()

    return field_id


def add_value(field_id, field_value, source, url, last_updated):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO knowledge_values
        (field_id, field_value, source, url, last_updated)
        VALUES (?, ?, ?, ?, ?)
    """, (field_id, field_value, source, url, last_updated))

    conn.commit()
    conn.close()

def get_topic(topic_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic_id, topic_name, category, description
        FROM knowledge_topics
        WHERE LOWER(topic_name)=LOWER(?)
    """, (topic_name,))

    result = cursor.fetchone()
    conn.close()

    return result


def get_topic_fields(topic_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            knowledge_fields.field_name,
            knowledge_values.field_value,
            knowledge_values.source,
            knowledge_values.url,
            knowledge_values.last_updated
        FROM knowledge_fields
        JOIN knowledge_values
        ON knowledge_fields.field_id = knowledge_values.field_id
        WHERE knowledge_fields.topic_id = ?
    """, (topic_id,))

    result = cursor.fetchall()
    conn.close()

    return result

def get_all_topics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic_id, topic_name
        FROM knowledge_topics
    """)

    topics = cursor.fetchall()

    conn.close()

    return topics

def get_search_records():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            knowledge_topics.topic_id,
            knowledge_topics.topic_name,
            knowledge_fields.field_name,
            knowledge_values.field_value
        FROM knowledge_topics
        JOIN knowledge_fields
            ON knowledge_topics.topic_id = knowledge_fields.topic_id
        JOIN knowledge_values
            ON knowledge_fields.field_id = knowledge_values.field_id
    """)

    records = cursor.fetchall()
    conn.close()
    return records


def get_programmes():

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM academic_programmes
        ORDER BY id ASC
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def add_programme(
    programme,
    specialization,
    level,
    college,
    department,
    duration,
    eligibility,
    intake,
    fee,
    admission_process,
    selection_process,
    overview,
    subject_overview,
    programme_type,
    school,
    campus,
    source,
    url,
    last_updated
):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO academic_programmes (
            programme,
            specialization,
            level,
            college,
            department,
            duration,
            programme_type,
            school,
            campus,
            eligibility,
            intake,
            fee,
            admission_process,
            selection_process,
            overview,
            subject_overview,
            source,
            url,
            last_updated
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        programme,
        specialization,
        level,
        college,
        department,
        duration,
        programme_type,
        school,
        campus,
        eligibility,
        intake,
        fee,
        admission_process,
        selection_process,
        overview,
        subject_overview,
        source,
        url,
        last_updated
    ))

    conn.commit()
    conn.close()


def delete_programme(programme_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM academic_programmes
        WHERE id = ?
    """, (programme_id,))

    conn.commit()
    conn.close()

def get_programme(programme_id):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM academic_programmes
        WHERE id = ?
    """, (programme_id,))
    programme = cursor.fetchone()
    conn.close()
    return programme

def update_programme(
    programme_id,
    programme,
    specialization,
    level,
    college,
    department,
    duration,
    programme_type,
    school,
    campus,
    eligibility,
    intake,
    fee,
    admission_process,
    selection_process,
    overview,
    subject_overview,
    source,
    url,
    last_updated
):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE academic_programmes
        SET
            programme = ?,
            specialization = ?,
            level = ?,
            college = ?,
            department = ?,
            duration = ?,
            programme_type = ?,
            school = ?,
            campus = ?,
            eligibility = ?,
            intake = ?,
            fee = ?,
            admission_process = ?,
            selection_process = ?,
            overview = ?,
            subject_overview = ?,
            source = ?,
            url = ?,
            last_updated = ?
        WHERE id = ?
    """, (
        programme,
        specialization,
        level,
        college,
        department,
        duration,
        programme_type,
        school,
        campus,
        eligibility,
        intake,
        fee,
        admission_process,
        selection_process,
        overview,
        subject_overview,
        source,
        url,
        last_updated,
        programme_id
    ))
    conn.commit()
    conn.close()

def get_colleges():

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM college_master
        ORDER BY college_id ASC
    """)

    colleges = cursor.fetchall()

    conn.close()

    return colleges


def get_college(college_id):

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM college_master
        WHERE college_id = ?
    """, (college_id,))

    college = cursor.fetchone()

    conn.close()

    return college


def add_college(
    college_name,
    short_name,
    university,
    established,
    type,
    campus,
    address,
    district,
    state,
    principal,
    overview,
    departments,
    programmes_offered,
    library,
    hostel,
    laboratories,
    sports,
    ncc,
    nss,
    facilities,
    website,
    google_maps,
    official_email
):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO college_master (
            college_name,
            short_name,
            university,
            established,
            type,
            campus,
            address,
            district,
            state,
            principal,
            overview,
            departments,
            programmes_offered,
            library,
            hostel,
            laboratories,
            sports,
            ncc,
            nss,
            facilities,
            website,
            google_maps,
            official_email
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?
        )
    """, (
        college_name,
        short_name,
        university,
        established,
        type,
        campus,
        address,
        district,
        state,
        principal,
        overview,
        departments,
        programmes_offered,
        library,
        hostel,
        laboratories,
        sports,
        ncc,
        nss,
        facilities,
        website,
        google_maps,
        official_email
    ))

    conn.commit()
    conn.close()


def update_college(
    college_id,
    college_name,
    short_name,
    university,
    established,
    type,
    campus,
    address,
    district,
    state,
    principal,
    overview,
    departments,
    programmes_offered,
    library,
    hostel,
    laboratories,
    sports,
    ncc,
    nss,
    facilities,
    website,
    google_maps,
    official_email
):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE college_master
        SET
            college_name = ?,
            short_name = ?,
            university = ?,
            established = ?,
            type = ?,
            campus = ?,
            address = ?,
            district = ?,
            state = ?,
            principal = ?,
            overview = ?,
            departments = ?,
            programmes_offered = ?,
            library = ?,
            hostel = ?,
            laboratories = ?,
            sports = ?,
            ncc = ?,
            nss = ?,
            facilities = ?,
            website = ?,
            google_maps = ?,
            official_email = ?
        WHERE college_id = ?
    """, (
        college_name,
        short_name,
        university,
        established,
        type,
        campus,
        address,
        district,
        state,
        principal,
        overview,
        departments,
        programmes_offered,
        library,
        hostel,
        laboratories,
        sports,
        ncc,
        nss,
        facilities,
        website,
        google_maps,
        official_email,
        college_id
    ))

    conn.commit()
    conn.close()


def delete_college(college_id):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM college_master
        WHERE college_id = ?
    """, (college_id,))

    conn.commit()
    conn.close()


def get_faculty_members(department=None, active_only=True):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM faculty WHERE 1=1"
    params = []

    if active_only:
        query += " AND is_active = 1"

    if department:
        query += " AND department LIKE ?"
        params.append(f"%{department}%")

    query += " ORDER BY department, name"

    cursor.execute(query, params)
    members = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return members


def add_faculty_member(name, department, designation="", email="",
                       phone="", office=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO faculty
        (name, department, designation, email, phone, office)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, department, designation, email, phone, office))

    conn.commit()
    conn.close()


def get_faculty_member(faculty_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM faculty WHERE faculty_id = ?",
        (faculty_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def update_faculty_member(faculty_id, name, department, designation="",
                          email="", phone="", office=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE faculty
        SET name = ?,
            department = ?,
            designation = ?,
            email = ?,
            phone = ?,
            office = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE faculty_id = ?
    """, (name, department, designation, email, phone, office, faculty_id))

    conn.commit()
    conn.close()


def deactivate_faculty_member(faculty_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE faculty
        SET is_active = 0,
            updated_at = CURRENT_TIMESTAMP
        WHERE faculty_id = ?
    """, (faculty_id,))

    conn.commit()
    conn.close()
