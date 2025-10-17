"""AI prompt templates for Daily Brief."""

# Article selection system prompt
SELECTION_SYSTEM_PROMPT = """You are an expert news editor for a personalized daily briefing.
Your goal: Select the MOST important and relevant articles.

Criteria:
1. Impact: Will this matter to the user?
2. Timeliness: Is this breaking/recent news?
3. Uniqueness: Does it offer new information?
4. Actionability: Can the user act on this?
5. Relevance: Matches user interests?

Return JSON:
{
  "selected": [
    {
      "id": "article_id",
      "reason": "1-sentence justification",
      "priority": 1-10
    }
  ],
  "rejected": ["id1", "id2"],
  "summary": "Brief rationale for selections"
}
"""

# Article selection user prompt template
SELECTION_USER_PROMPT_TEMPLATE = """User Profile:
- Interests: {interests}
- Previously liked topics: {liked_topics}
- Previously disliked: {disliked_topics}

Candidate Articles ({count}):
{articles_json}

Task: Select exactly {target_count} articles.
Balance: Mix of breaking news, deep analysis, and user interests.
Diversity: Multiple topics, avoid repetition.
"""

# Script generation system prompt
SCRIPT_SYSTEM_PROMPT = """You are a professional podcast host creating an audio news briefing.

Style Guide:
- Conversational yet authoritative
- Clear pronunciation (avoid jargon without explanation)
- Natural pacing with <pause> tags
- Engaging transitions between stories
- Appropriate emotional tone per story

Structure:
1. Opening: Warm greeting, date, brief preview
2. Stories: Each with context, key facts, implications
3. Transitions: Smooth connections between topics
4. Closing: Summary, call-to-action if relevant

Duration: Target {duration} minutes
Reading speed: ~150 words/minute
Format: Plain text (will be converted to audio)
"""

# Script generation user prompt template
SCRIPT_USER_PROMPT_TEMPLATE = """Generate a {duration}-minute audio briefing from these articles:

{articles_with_summaries}

User Preferences:
- Detail level: {detail_level}
- Tone: {tone}
- Language: {language}
- Special interests: {interests}

Instructions:
- Start with most important/breaking news
- Use clear, concise language
- Add <pause> tags for natural breaks
- Include context for technical terms
- End on a positive or forward-looking note

Generate the complete script now:
"""

# Summary generation prompt
SUMMARY_PROMPT_TEMPLATE = """Summarize this article in 2-3 sentences for an audio briefing:

Title: {title}
Content: {content}

Summary:"""


def get_selection_prompt(
    articles: list[dict],
    interests: list[str],
    target_count: int,
    liked_topics: list[str] | None = None,
    disliked_topics: list[str] | None = None,
) -> str:
    """Generate article selection prompt.

    Args:
        articles: List of article dictionaries
        interests: User interests
        target_count: Number of articles to select
        liked_topics: Previously liked topics
        disliked_topics: Previously disliked topics

    Returns:
        Formatted prompt string

    """
    import json

    liked = ", ".join(liked_topics) if liked_topics else "None"
    disliked = ", ".join(disliked_topics) if disliked_topics else "None"
    interests_str = ", ".join(interests) if interests else "General"

    # Format articles for prompt
    article_list = []
    for idx, article in enumerate(articles, 1):
        article_list.append({
            "id": article.get("id", f"article_{idx}"),
            "title": article.get("title", ""),
            "summary": article.get("summary", "")[:200],  # Truncate for token efficiency
            "topics": article.get("topics", []),
            "published": article.get("published_at", ""),
        })

    articles_json = json.dumps(article_list, indent=2, ensure_ascii=False)

    return SELECTION_USER_PROMPT_TEMPLATE.format(
        interests=interests_str,
        liked_topics=liked,
        disliked_topics=disliked,
        count=len(articles),
        target_count=target_count,
        articles_json=articles_json,
    )


def get_script_prompt(
    articles: list[dict],
    duration: int,
    detail_level: str = "balanced",
    tone: str = "professional",
    language: str = "en",
    interests: list[str] | None = None,
) -> str:
    """Generate script generation prompt.

    Args:
        articles: List of selected articles
        duration: Target duration in minutes
        detail_level: Level of detail (summary/balanced/detailed)
        tone: Tone of voice (professional/casual/enthusiastic)
        language: Language code
        interests: User interests

    Returns:
        Formatted prompt string

    """
    # Format articles with summaries
    articles_text = []
    for idx, article in enumerate(articles, 1):
        articles_text.append(f"""
Story {idx}: {article.get('title', '')}
Source: {article.get('source', 'Unknown')}
Summary: {article.get('summary', '')}
URL: {article.get('url', '')}
""")

    articles_with_summaries = "\n".join(articles_text)
    interests_str = ", ".join(interests) if interests else "General"

    return SCRIPT_USER_PROMPT_TEMPLATE.format(
        duration=duration,
        articles_with_summaries=articles_with_summaries,
        detail_level=detail_level,
        tone=tone,
        language=language,
        interests=interests_str,
    )


def get_summary_prompt(title: str, content: str) -> str:
    """Generate summary prompt for an article.

    Args:
        title: Article title
        content: Article content

    Returns:
        Formatted prompt string

    """
    # Truncate content if too long
    max_content_length = 1000
    truncated_content = content[:max_content_length]
    if len(content) > max_content_length:
        truncated_content += "..."

    return SUMMARY_PROMPT_TEMPLATE.format(
        title=title,
        content=truncated_content,
    )
