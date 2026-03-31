import pytest
import json
import sys
import os

sys.path.insert(0, '.')
from devops_tool import system_info

def test_system_info_keys():
    """Verifie que system_info retourne les bonnes clés"""
    info = system_info()
    assert "hostname" in info
    assert "disk" in info
    assert "memory" in info
    assert "uptime" in info

def test_disk_info_keys():
    """Vérifie la structure des infos disques"""
    info = system_info()
    assert "total" in info["disk"]
    assert "used" in info["disk"]
    assert "dispo" in info["disk"]
    assert "percent" in info["disk"]

def test_memory_info_keys():
    """Vérifie la structure des infos mémoire"""
    info = system_info()
    assert "total" in info["memory"]
    assert "available" in info["memory"]

def test_hostname_not_empty():
    """Vérifie que le hostname n'est pas vide"""
    info = system_info()
    assert info["hostname"] != ""
    assert info["hostname"] is not None