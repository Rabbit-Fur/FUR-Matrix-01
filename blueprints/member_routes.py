from flask import Blueprint, render_template
from web.auth.decorators import r3_required

member_bp = Blueprint("member", __name__, url_prefix="/members")

@r3_required
@member_bp.route('/member_dashboard')
def member_dashboard():
    return render_template("member/member_dashboard.html")

@r3_required
@member_bp.route('/member_downloads')
def member_downloads():
    return render_template("member/member_downloads.html")

@r3_required
@member_bp.route('/member_stats')
def member_stats():
    return render_template("member/member_stats.html")

@r3_required
@member_bp.route('/settings')
def settings():
    return render_template("member/settings.html")

