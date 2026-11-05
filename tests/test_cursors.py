from pathlib import Path

import pytest

from src import cursors


@pytest.mark.parametrize("name", cursors.PACKS)
def test_every_file_of_the_pack_exists(name):
    # Ловит опечатки: в паках бывают имена вроде "unavailiable.cur" и "link-acount.cur"
    for role, path in cursors.role_paths(name).items():
        assert not path or Path(path).is_file(), f"{name}: {role} -> {path}"


@pytest.mark.parametrize("name", cursors.PACKS)
def test_pack_uses_only_known_roles(name):
    assert set(cursors.PACKS[name]) <= set(cursors.ROLES)


def test_missing_role_means_default_windows_cursor():
    files = cursors.role_paths("dota")
    assert files["Arrow"].endswith("Dota1.cur")
    assert files["Hand"] == ""
    assert list(files) == list(cursors.ROLES)  # порядок важен для схемы


def test_next_pack_goes_in_a_circle():
    names = list(cursors.PACKS)
    assert cursors.next_pack(names[0]) == names[1]
    assert cursors.next_pack(names[-1]) == names[0]
    assert cursors.next_pack(None) == names[0]


def test_random_pack_is_never_the_current_one():
    for _ in range(50):
        assert cursors.random_pack("dota") != "dota"
