from html import escape


def topics_card_html(top_topics):
    topic_chips = "".join(
        f'<span class="cl-topic-chip">{escape(str(topic))}</span>'
        for topic in top_topics
    )
    if not topic_chips:
        topic_chips = '<span class="cl-summary-empty">Sin datos</span>'
    return (
        '<div class="cl-topic-card">'
        '<div class="cl-summary-label">Temas principales</div>'
        f'<div class="cl-topic-list">{topic_chips}</div>'
        "</div>"
    )


def sentiment_distribution_html(analyses):
    sentiment_labels = {
        "positive": ("Positivo", "positive"),
        "neutral": ("Neutral", "neutral"),
        "negative": ("Negativo", "negative"),
    }
    sentiment_counts = {}
    for analysis in analyses:
        sentiment = str(analysis.get("sentiment") or "").strip().casefold()
        if sentiment:
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

    total = sum(sentiment_counts.values())
    heading = (
        '<div class="cl-sentiment-chart__heading">'
        '<div><div class="cl-sentiment-chart__eyebrow">PANORAMA DE SENTIMIENTO</div>'
        '<div class="cl-sentiment-chart__title">Distribución de sentimientos</div></div>'
    )
    if not total:
        return (
            '<div class="cl-sentiment-chart">'
            f'{heading}<span class="cl-sentiment-chart__total">0 análisis</span></div>'
            '<p class="cl-sentiment-chart__empty">No hay datos de sentimiento para esta ejecución.</p>'
            "</div>"
        )

    sentiment_order = ("positive", "neutral", "negative")
    ordered_sentiments = [
        sentiment for sentiment in sentiment_order if sentiment in sentiment_counts
    ]
    ordered_sentiments.extend(sorted(set(sentiment_counts) - set(sentiment_order)))
    leading_count = max(sentiment_counts.values())
    rows = []
    for sentiment in ordered_sentiments:
        count = sentiment_counts[sentiment]
        percentage = count / total * 100
        label, tone = sentiment_labels.get(
            sentiment,
            (sentiment.replace("_", " ").capitalize(), "other"),
        )
        is_leading = count == leading_count
        leading_badge = (
            '<span class="cl-sentiment-row__badge">Mayor porcentaje</span>'
            if is_leading
            else ""
        )
        rows.append(
            f'<div class="cl-sentiment-row{" cl-sentiment-row--leading" if is_leading else ""}">'
            '<div class="cl-sentiment-row__meta">'
            f'<span class="cl-sentiment-row__label">{escape(label)}{leading_badge}</span>'
            f'<span class="cl-sentiment-row__value">{count} · {percentage:.1f}%</span>'
            "</div>"
            '<div class="cl-sentiment-track">'
            f'<div class="cl-sentiment-bar cl-sentiment-bar--{tone}" '
            f'style="width: {percentage:.1f}%" role="progressbar" '
            f'aria-label="{escape(label)}" aria-valuenow="{count}" '
            f'aria-valuemin="0" aria-valuemax="{total}"></div>'
            "</div></div>"
        )
    return (
        '<div class="cl-sentiment-chart">'
        f'{heading}<span class="cl-sentiment-chart__total">{total} análisis</span></div>'
        f'<div class="cl-sentiment-chart__rows">{"".join(rows)}</div>'
        "</div>"
    )
