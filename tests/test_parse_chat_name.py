from unittest import TestCase

import pytest

from src.parse_chat_name import get_course_name

cases_course_groups = [
    ("[S24] Databases", "Databases"),
    (
        "[S24] Distributed and Network Programming",
        "Distributed and Network Programming",
    ),
    ("[S24] Intro to ML", "Intro to ML"),
    (
        "[S24] System and Network Administration",
        "System and Network Administration",
    ),
    (
        "[F24] Network and Cyber Security / Сетевая и кибербезопасность",
        "Network and Cyber Security",
    ),
    ("[F24] Information Retrieval / Информационный поиск", "Information Retrieval"),
    (
        "[F24] Software Architecture / Архитектура программного обеспечения",
        "Software Architecture",
    ),
    (
        "[F24] Fundamentals of Information Security / Основные принципы информационной безопасности",
        "Fundamentals of Information Security",
    ),
    ("[s23] Linear Algebra II", "Linear Algebra II"),
    ("[Sum24] Безопасность жизнедеятельности", "Безопасность жизнедеятельности"),
    (
        "[F24] Introduction to Functional Programming and Scala Language",
        "Introduction to Functional Programming and Scala Language",
    ),
    ("[F23] Differential Equations Students", "Differential Equations"),
    ("[S24] Databases", "Databases"),
    ("[S23] Math Analysis II (Discussions)", "Math Analysis II"),
    ("[Sum24] MLOps Engineering / Разработка и внедрение ML-решений", "MLOps Engineering"),
    (
        "[Sum24] Personal Efficiency Skills of IT-specialist / Навыки личной эффективности ИТ-специалиста",
        "Personal Efficiency Skills of IT-specialist",
    ),
    ("[Sum24] Practicum Project / Прикладной проект", "Practicum Project"),
    ("[Sum23] History / История (история России, всеобщая история) Students", "History"),
    ("[S24] Distributed and Network Programming", "Distributed and Network Programming"),
    ("[S24] Intro to ML", "Intro to ML"),
    ("[S24] System and Network Administration", "System and Network Administration"),
    ("[S24] Networks Students", "Networks"),
    ("[F23] Philosophy II (Introduction to AI) Students", "Philosophy II"),
    ("[F23] Probability & Statistics", "Probability & Statistics"),
    ("[F23] Probability and Statistics Students", "Probability and Statistics"),
    ("[F23] Operating Systems Students", "Operating Systems"),
    ("[S23] Data Structures and Algorithms Students", "Data Structures and Algorithms"),
    ("[F23] Introduction to Optimization Students", "Introduction to Optimization"),
    ("[F23] Physics I (Mechanics) Students", "Physics I"),
    ("[F22] AGLA I", "AGLA I"),
    ("[S23]Theoretical Sports / Физическая культура и спорт", "Theoretical Sports"),
    ("[Sum23] Software Project Students", "Software Project"),
    ("[Sum23] Software Project", "Software Project"),
    (
        "[Sum23] Introduction to Robot Operating System: Basics, Motion, and Vision Students",
        "Introduction to Robot Operating System: Basics, Motion, and Vision",
    ),
    ("[S23] Theoretical Computer Science Students", "Theoretical Computer Science"),
    ("[S23] Sport electives", "Sport electives"),
    ("[S23] Data Structures and Algorithms", "Data Structures and Algorithms"),
    (
        "[S23] Software Systems Analysis and Design / Проектирование и анализ программных систем",
        "Software Systems Analysis and Design",
    ),
    ("[F22] Introduction to Programming", "Introduction to Programming"),
    ("[F22] Logic and Discrete Mathematics", "Logic and Discrete Mathematics"),
]


@pytest.mark.parametrize("input_, desired", cases_course_groups)
def test_location_parser(input_, desired: str):
    _ = TestCase()
    _.maxDiff = None

    course_name = get_course_name(input_)
    assert course_name == desired
