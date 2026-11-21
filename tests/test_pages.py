"""Smoke tests: every app page must execute end-to-end without exception.
Uses Streamlit's official AppTest harness (real ScriptRunner execution).
Run:  python -m pytest tests/test_pages.py -v
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from streamlit.testing.v1 import AppTest

PAGES = [
    "1_🏠_Home_Research_Overview.py",
    "2_📖_Problem_&_Literature.py",
    "3_🗂️_Data_Sources_&_Dictionary.py",
    "4_🧹_Data_Collection_&_Cleaning.py",
    "5_📈_Exploratory_Data_Analysis.py",
    "6_📊_Stylized_Facts_&_Risk.py",
    "7_🕸️_PGM_Learning_Centre.py",
    "8_🔗_Inferred_Causality_Explorer.py",
    "11_🔮_Forecasting_&_Investment_Insights.py",
    "10_👤_Methodology_&_About.py",
]


@pytest.mark.parametrize("page", PAGES)
def test_page_executes_without_exception(page):
    at = AppTest.from_file(os.path.join(ROOT, "pages", page), default_timeout=120)
    at.run()
    assert not at.exception, f"{page} raised: {at.exception}"


def test_main_app_executes():
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=120)
    at.run()
    assert not at.exception
