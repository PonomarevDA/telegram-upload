#!/usr/bin/env python3
import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from deploy import resolve_files

def test_resolve_files_relative_literal(tmp_path : Path, monkeypatch):
    test_file = tmp_path / "test.txt"
    test_file.write_text("sample content")

    monkeypatch.chdir(tmp_path)
    input_files = ["test.txt"]
    result = resolve_files(input_files)

    assert len(result) == 1
    assert result[0].resolve() == test_file.resolve()

def test_resolve_files_absolute_literal(tmp_path : Path, monkeypatch):
    test_file = tmp_path / "test.txt"
    test_file.write_text("sample content")

    input_files = [test_file]
    result = resolve_files(input_files)

    assert len(result) == 1
    assert result[0].resolve() == test_file.resolve()

def test_resolve_files_pattern(tmp_path : Path, monkeypatch):
    test_file = tmp_path / "test.txt"
    test_file.write_text("sample content")

    monkeypatch.chdir(tmp_path)
    input_files = ["*.txt"]
    result = resolve_files(input_files)

    assert len(result) == 1
    assert result[0].resolve() == test_file.resolve()

def test_resolve_files_no_files():
    with pytest.raises(FileNotFoundError):
        resolve_files("Not a file")
