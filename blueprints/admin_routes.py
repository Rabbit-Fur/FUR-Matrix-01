from flask import Blueprint, render_template
from web.auth.decorators import r4_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@r4_required
@admin_bp.route('/admin')
def admin():
    return render_template("admin/admin.html")

@r4_required
@admin_bp.route('/calendar')
def calendar():
    return render_template("admin/calendar.html")

@r4_required
@admin_bp.route('/create_event')
def create_event():
    return render_template("admin/create_event.html")

@r4_required
@admin_bp.route('/dashboard')
def dashboard():
    return render_template("admin/dashboard.html")

@r4_required
@admin_bp.route('/diplomacy')
def diplomacy():
    return render_template("admin/diplomacy.html")

@r4_required
@admin_bp.route('/downloads')
def downloads():
    return render_template("admin/downloads.html")

@r4_required
@admin_bp.route('/edit_event')
def edit_event():
    return render_template("admin/edit_event.html")

@r4_required
@admin_bp.route('/events')
def events():
    return render_template("admin/events.html")

@r4_required
@admin_bp.route('/leaderboards')
def leaderboards():
    return render_template("admin/leaderboards.html")

@r4_required
@admin_bp.route('/participants')
def participants():
    return render_template("admin/participants.html")

@r4_required
@admin_bp.route('/settings')
def settings():
    return render_template("admin/settings.html")

@r4_required
@admin_bp.route('/tools')
def tools():
    return render_template("admin/tools.html")

@r4_required
@admin_bp.route('/translations_editor')
def translations_editor():
    return render_template("admin/translations_editor.html")

