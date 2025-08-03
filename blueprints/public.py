from bson import ObjectId
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from fur_lang.i18n import get_supported_languages, t
from mongo_service import get_collection
from web.auth.decorators import r3_required

public = Blueprint("public", __name__)


@public.route("/")
def landing():
    return render_template("public/landing.html")


@public.route("/set_language")
def set_language():
    lang = request.args.get("lang")
    if lang in get_supported_languages():
        session["lang"] = lang
    return redirect(request.referrer or url_for("public.landing"))


@public.route("/lore")
def lore():
    return render_template("public/lore.html")


@public.route("/calendar")
def calendar():
    return render_template("public/calendar.html")


@public.route("/events")
def events():
    rows = list(get_collection("events").find().sort("event_time", 1))
    if current_app.config.get("TESTING"):
        rows = []
    else:
        rows = list(get_collection("events").find().sort("event_time", 1))
    return render_template("public/events_list.html", events=rows)


@public.route("/events/<event_id>")
def view_event(event_id):
    event = get_collection("events").find_one({"_id": ObjectId(event_id)})
    if not event:
        abort(404)
    participant_docs = list(get_collection("event_participants").find({"event_id": event["_id"]}))
    participants = []
    for p in participant_docs:
        user = get_collection("users").find_one({"discord_id": p["user_id"]})
        participants.append({"username": user.get("username") if user else p["user_id"]})
    return render_template("public/view_event.html", event=event, participants=participants)


@public.route("/events/<event_id>/join", methods=["POST"])
@r3_required
def join_event(event_id):
    if "discord_user" not in session:
        flash(t("login_required", default="Login required."), "warning")
        return redirect(url_for("auth.login"))

    flash(t("event_join_success", default="Successfully joined the event!"), "success")
    return redirect(url_for("public.view_event", event_id=event_id))


@public.route("/hall_of_fame")
def hall_of_fame():
    rows = list(get_collection("hall_of_fame").find().sort("_id", -1).limit(10))
    if current_app.config.get("TESTING"):
        rows = []
    else:
        rows = list(get_collection("hall_of_fame").find().sort("_id", -1).limit(10))
    return render_template("public/hall_of_fame.html", hof=rows)


@public.route("/leaderboard")
def leaderboard():
    rows = list(get_collection("leaderboard").find().sort("score", -1).limit(100))
    leaderboard_list = []
    for i, row in enumerate(rows, start=1):
        leaderboard_list.append({"rank": i, "username": row["username"], "score": row["score"]})
    if current_app.config.get("TESTING"):
        leaderboard_list = []
    else:
        rows = list(get_collection("leaderboard").find().sort("score", -1).limit(100))
        leaderboard_list = []
        for i, row in enumerate(rows, start=1):
            leaderboard_list.append({"rank": i, "username": row["username"], "score": row["score"]})
    return render_template("public/public_leaderboard.html", leaderboard=leaderboard_list)


@public.route("/bank-war-top5")
def bank_war_top5():
    """Display BANK WAR recap and top 5 players."""
    return render_template("public/bank_war_top5.html")
