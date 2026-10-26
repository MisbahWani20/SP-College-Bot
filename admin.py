from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from chatbot.knowledge_database import (
    get_programmes,
    add_programme,
    delete_programme,
    get_programme,
    update_programme,

    get_colleges,
    get_college,
    add_college,
    delete_college,
    update_college,

    get_faculty_members,
    add_faculty_member,
    get_faculty_member,
    update_faculty_member,
    deactivate_faculty_member,
)

load_dotenv()

admin = Blueprint("admin", __name__)

USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

@admin.route("/admin")
def login():

    return render_template(
        "admin/login.html"
    )


@admin.route("/admin/login", methods=["POST"])
def admin_login():

    username = request.form["username"]
    password = request.form["password"]

    if username == USERNAME and password == PASSWORD:

        session["admin"] = True

        return redirect(
            url_for("admin.dashboard")
        )

    return render_template(
        "admin/login.html",
        error="Invalid Username or Password"
    )

@admin.route("/admin/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )
    return render_template(
        "admin/dashboard.html"
    )

@admin.route("/admin/logout")
def logout():
    session.clear()
    return redirect(
        url_for("admin.login")
    )

@admin.route("/admin/programmes")
def programmes():
    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )
    programmes = get_programmes()

    return render_template(
        "admin/manage_programmes.html",
        programmes=programmes
    )
@admin.route("/admin/colleges")
def colleges():
    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )
    colleges = get_colleges()
    return render_template(
        "admin/manage_colleges.html",
        colleges=colleges
    )

@admin.route(
    "/admin/programmes/add",
    methods=["POST"]
)
def programme_add():
    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )
    add_programme(
        request.form["programme"],

        request.form.get(
            "specialization",
            ""
        ),

        request.form.get(
            "level",
            ""
        ),

        request.form.get(
            "college",
            ""
        ),

        request.form.get(
            "department",
            ""
        ),

        request.form.get(
            "duration",
            ""
        ),
        request.form.get(
            "eligibility",
             ""
        ),

        request.form.get(
            "intake",
            ""
        ),

        request.form.get(
            "fee",
            ""
        ),

        request.form.get(
            "admission_process",
            ""
        ),

        request.form.get(
            "selection_process",
            ""
        ),

        request.form.get(
            "overview",
            ""
        ),

        request.form.get(
            "subject_overview",
            ""
        ),
        request.form.get(
            "programme_type",
            ""
        ),

        request.form.get(
            "school",
            ""
        ),
        
        request.form.get(
            "campus",
            ""
        ),

        request.form.get(
            "source",
            ""
        ),

        request.form.get(
            "url",
            ""
        ),

        request.form.get(
            "last_updated",
            ""
        )
    )
    flash("Programme added successfully.", "success")
    return redirect(
        url_for("admin.programmes")
    )

@admin.route(
    "/admin/programmes/delete/<int:programme_id>"
)
def programme_delete(programme_id):
    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )
    delete_programme(
        programme_id
    )
    flash("Programme deleted successfully.", "success")
    return redirect(
        url_for("admin.programmes")
    )
@admin.route(
    "/admin/programmes/edit/<int:programme_id>"
)
def programme_edit(programme_id):

    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )

    programme = get_programme(
        programme_id
    )

    if not programme:
        flash(
            "Programme not found.",
            "error"
        )

        return redirect(
            url_for("admin.programmes")
        )

    return render_template(
        "admin/edit_programme.html",
        programme=programme
    )


@admin.route(
    "/admin/programmes/update/<int:programme_id>",
    methods=["POST"]
)
def programme_update(programme_id):

    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )

    update_programme(
        programme_id,

        request.form["programme"],

        request.form.get(
            "specialization",
            ""
        ),

        request.form.get(
            "level",
            ""
        ),

        request.form.get(
            "college",
            ""
        ),

        request.form.get(
            "department",
            ""
        ),

        request.form.get(
            "duration",
            ""
        ),

        request.form.get(
            "programme_type",
            ""
        ),

        request.form.get(
            "school",
            ""
        ),

        request.form.get(
            "campus",
            ""
        ),

        request.form.get(
            "eligibility",
            ""
        ),

        request.form.get(
            "intake",
            ""
        ),

        request.form.get(
            "fee",
            ""
        ),

        request.form.get(
            "admission_process",
            ""
        ),

        request.form.get(
            "selection_process",
            ""
        ),

        request.form.get(
            "overview",
            ""
        ),

        request.form.get(
            "subject_overview",
            ""
        ),

        request.form.get(
            "source",
            ""
        ),

        request.form.get(
            "url",
            ""
        ),

        request.form.get(
            "last_updated",
            ""
        )
    )
    flash(
        "Programme updated successfully.",
        "success"
    )
    return redirect(
        url_for("admin.programmes")
    )

@admin.route(
    "/admin/colleges/add",
    methods=["POST"]
)
def college_add():

    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )

    add_college(

        request.form["college_name"],

        request.form.get(
            "short_name",
            ""
        ),

        request.form.get(
            "university",
            ""
        ),

        request.form.get(
            "established",
            ""
        ),

        request.form.get(
            "type",
            ""
        ),

        request.form.get(
            "campus",
            ""
        ),

        request.form.get(
            "address",
            ""
        ),

        request.form.get(
            "district",
            ""
        ),

        request.form.get(
            "state",
            ""
        ),

        request.form.get(
            "principal",
            ""
        ),

        request.form.get(
            "overview",
            ""
        ),

        request.form.get(
            "departments",
            ""
        ),

        request.form.get(
            "programmes_offered",
            ""
        ),

        request.form.get(
            "library",
            ""
        ),

        request.form.get(
            "hostel",
            ""
        ),

        request.form.get(
            "laboratories",
            ""
        ),

        request.form.get(
            "sports",
            ""
        ),

        request.form.get(
            "ncc",
            ""
        ),

        request.form.get(
            "nss",
            ""
        ),

        request.form.get(
            "facilities",
            ""
        ),

        request.form.get(
            "website",
            ""
        ),

        request.form.get(
            "google_maps",
            ""
        ),

        request.form.get(
            "official_email",
            ""
        )
    )

    flash(
        "College added successfully.",
        "success"
    )

    return redirect(
        url_for("admin.colleges")
    )
@admin.route(
    "/admin/colleges/delete/<int:college_id>"
)
def college_delete(college_id):

    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )

    delete_college(college_id)

    flash(
        "College deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.colleges")
    )
@admin.route(
    "/admin/colleges/edit/<int:college_id>"
)
def college_edit(college_id):

    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )

    college = get_college(college_id)

    if not college:

        flash(
            "College not found.",
            "error"
        )

        return redirect(
            url_for("admin.colleges")
        )

    return render_template(
        "admin/edit_college.html",
        college=college
    )
@admin.route(
    "/admin/colleges/update/<int:college_id>",
    methods=["POST"]
)
def college_update(college_id):

    if not session.get("admin"):
        return redirect(
            url_for("admin.login")
        )

    update_college(

        college_id,

        request.form["college_name"],

        request.form.get(
            "short_name",
            ""
        ),

        request.form.get(
            "university",
            ""
        ),

        request.form.get(
            "established",
            ""
        ),

        request.form.get(
            "type",
            ""
        ),

        request.form.get(
            "campus",
            ""
        ),

        request.form.get(
            "address",
            ""
        ),

        request.form.get(
            "district",
            ""
        ),

        request.form.get(
            "state",
            ""
        ),

        request.form.get(
            "principal",
            ""
        ),

        request.form.get(
            "overview",
            ""
        ),

        request.form.get(
            "departments",
            ""
        ),

        request.form.get(
            "programmes_offered",
            ""
        ),

        request.form.get(
            "library",
            ""
        ),

        request.form.get(
            "hostel",
            ""
        ),

        request.form.get(
            "laboratories",
            ""
        ),

        request.form.get(
            "sports",
            ""
        ),

        request.form.get(
            "ncc",
            ""
        ),

        request.form.get(
            "nss",
            ""
        ),

        request.form.get(
            "facilities",
            ""
        ),

        request.form.get(
            "website",
            ""
        ),

        request.form.get(
            "google_maps",
            ""
        ),

        request.form.get(
            "official_email",
            ""
        )
    )

    flash(
        "College updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin.colleges")
    )


@admin.route("/admin/faculty")
def faculty():
    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    faculty_members = get_faculty_members(active_only=False)

    return render_template(
        "admin/manage_faculty.html",
        faculty_members=faculty_members
    )


@admin.route("/admin/faculty/add", methods=["POST"])
def faculty_add():
    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()

    if not name or not department:
        flash("Name and department are required.", "error")
        return redirect(url_for("admin.faculty"))

    add_faculty_member(
        name,
        department,
        request.form.get("designation", "").strip(),
        request.form.get("email", "").strip(),
        request.form.get("phone", "").strip(),
        request.form.get("office", "").strip()
    )

    flash("Faculty member added successfully.", "success")
    return redirect(url_for("admin.faculty"))


@admin.route("/admin/faculty/edit/<int:faculty_id>")
def faculty_edit(faculty_id):
    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    member = get_faculty_member(faculty_id)

    if not member:
        flash("Faculty member not found.", "error")
        return redirect(url_for("admin.faculty"))

    return render_template(
        "admin/edit_faculty.html",
        member=member
    )


@admin.route("/admin/faculty/update/<int:faculty_id>", methods=["POST"])
def faculty_update(faculty_id):
    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()

    if not name or not department:
        flash("Name and department are required.", "error")
        return redirect(
            url_for("admin.faculty_edit", faculty_id=faculty_id)
        )

    update_faculty_member(
        faculty_id,
        name,
        department,
        request.form.get("designation", "").strip(),
        request.form.get("email", "").strip(),
        request.form.get("phone", "").strip(),
        request.form.get("office", "").strip()
    )

    flash("Faculty member updated successfully.", "success")
    return redirect(url_for("admin.faculty"))


@admin.route("/admin/faculty/deactivate/<int:faculty_id>", methods=["POST"])
def faculty_deactivate(faculty_id):
    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    deactivate_faculty_member(faculty_id)

    flash("Faculty member deactivated successfully.", "success")
    return redirect(url_for("admin.faculty"))
