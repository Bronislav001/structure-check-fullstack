from app.services.analyze import analyze_text_against_template, normalize_for_match
from app.services.template import get_default_template


def test_normalize_for_match_strips_numbering_and_punctuation():
    assert normalize_for_match('1. Введение:') == 'введение'


def test_analyze_text_reports_missing_sections_and_ok_flag():
    template = get_default_template()
    text = """
1. Введение
2. Теоретическая часть
3. Практическая часть
"""
    result = analyze_text_against_template(text, template)
    assert result['ok'] is False
    assert result['found'][:3] == ['Введение', 'Теоретическая часть', 'Практическая часть']
    assert 'Методология' in result['missing']


def test_analyze_text_accepts_full_template():
    template = get_default_template()
    text = '\n'.join(template)
    result = analyze_text_against_template(text, template)
    assert result['ok'] is True
    assert result['missing'] == []
