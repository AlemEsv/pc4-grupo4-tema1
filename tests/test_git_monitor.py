from unittest.mock import patch
from scripts.git_monitor import run_cmd, get_local_commit, get_remote_commit, log_error
import scripts.git_monitor


def test_run_cmd_git_rev_parse():
    # Simulamos que subprocess.run devuelve el hash de commit f0c2a8b1234567890abcdef
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "f0c2a8b1234567890abcdef\n"
        mock_run.return_value.stderr = ""
        stdout, stderr = run_cmd("git rev-parse HEAD")
        assert stdout == "f0c2a8b1234567890abcdef"
        assert stderr == ""


def test_get_local_commit():
    # Mockeamos run_cmd dentro de git_monitor
    with patch("scripts.git_monitor.run_cmd") as mock_run:
        mock_run.return_value = ("asdasdasd", "")
        assert get_local_commit() == "asdasdasd"


def test_get_remote_commit():
    # salida de git ls-remote
    with patch("scripts.git_monitor.run_cmd") as mock_run:
        mock_run.return_value = ("asdasdasd\trefs/heads/main", "")
        assert get_remote_commit() == "asdasdasd"


def test_log_error(tmp_path):
    log_file = tmp_path / "monitor_errors.log"
    msg = "Error simulado para test"
    original_log_file = scripts.git_monitor.LOG_FILE
    try:
        scripts.git_monitor.LOG_FILE = str(log_file)
        log_error(msg)
        with open(log_file, encoding="utf-8") as f:
            contenido = f.read()
        assert msg in contenido
    finally:
        scripts.git_monitor.LOG_FILE = original_log_file
