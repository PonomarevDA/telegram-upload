#!/usr/bin/env python3
import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from deploy import BuildTypeEnum, GitInfo, resolve_files, resolve_target

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

def test_resolve_target_supports_legacy_chat_id():
    assert resolve_target(None, "12345", BuildTypeEnum.DEV, None) == "12345"

def test_resolve_target_prefers_target_over_legacy_chat_id():
    target = '{"channel_id": "channel", "Alice": "alice-chat"}'
    git_info = GitInfo(
        commit_sha="abcdef12",
        commit_date="2026-04-14",
        committer_name="Alice",
        committer_email="alice@example.com",
        branch_name="feature",
        latest_tag="v1.0.0",
        commit_history=["change"],
    )

    assert resolve_target(target, "legacy-chat", BuildTypeEnum.DEV, git_info) == "alice-chat"

def test_resolve_target_uses_channel_for_stable_builds():
    target = '{"channel_id": "channel", "Alice": "alice-chat"}'
    git_info = GitInfo(
        commit_sha="abcdef12",
        commit_date="2026-04-14",
        committer_name="Alice",
        committer_email="alice@example.com",
        branch_name="main",
        latest_tag="v1.0.0",
        commit_history=["change"],
    )

    assert resolve_target(target, None, BuildTypeEnum.MAIN, git_info) == "channel"
