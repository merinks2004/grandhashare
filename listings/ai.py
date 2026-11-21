from django.conf import settings
from google import genai
from google.genai import types


class AIUnavailable(Exception):
    """Raised when the AI service cannot give an answer."""


SYSTEM_PROMPT = (
    "You write short listing descriptions for a used-textbook marketplace "
    "for Kerala college students. Write 2 to 3 plain, friendly sentences. "
    "Use ONLY the details you are given. Do not invent facts such as notes, "
    "highlighting, missing pages, price, or edition. Do not mention contact "
    "details. Output only the description text."
)


def generate_description(title, author, edition, subject, condition, course_name):
    if not settings.GEMINI_API_KEY:
        raise AIUnavailable("AI is not configured.")

    prompt = (
        f"Title: {title}\nAuthor: {author}\nEdition: {edition or 'not given'}\n"
        f"Subject: {subject}\nCourse: {course_name or 'not given'}\n"
        f"Condition: {condition}"
    )
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1000,
                temperature=0.4,
            ),
        )
    except Exception as exc:  # network error, bad key, wrong model, quota
        raise AIUnavailable("The AI service is not available right now.") from exc

    text = (response.text or "").strip()
    if not text:
        raise AIUnavailable("The AI service returned no text.")
    return text[:600]