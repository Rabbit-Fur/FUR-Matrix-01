async def leaderboard(ctx):
    try:
        scores = db.get_scores()  # DB-Logik ausgelagert
        if not scores:
            await ctx.send(t("Keine Einträge im Leaderboard gefunden."))
            return
        await ctx.send(t("Leaderboard:") + "\n" + format_scores(scores))
    except Exception as e:
        await ctx.send(t("Fehler beim Abruf des Leaderboards: ") + str(e))