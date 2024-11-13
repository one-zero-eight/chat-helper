import re


def get_course_name(chat_name: str) -> str:
    # Regex pattern to remove the prefix like [S24], [F23], etc., and any suffix after " / "
    match = re.match(r"\[.*?\]\s*([^\s/]+.*?)(\s*/.*)?$", chat_name)
    if match:
        course_name = match.group(1).strip()
        # Remove "Students" if it appears at the end
        if course_name.endswith("Students"):
            course_name = course_name.rsplit(" ", 1)[0].strip()
        # Remove any trailing parentheses and their content
        course_name = re.sub(r"\s*\(.*?\)$", "", course_name).strip()
        return course_name
    return chat_name  # Return as is if pattern doesn't match


def get_semester(chat_name: str) -> str | None:
    match = re.match(r"\[.*?\]", chat_name)

    if match:
        return match.group(0).strip("[] ").capitalize()

    return None
