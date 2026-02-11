import pathlib
import pytest

from stfc_parser.parser_stub import parse_filename_to_session_info


def get_log_files():
    # Adjust path as needed
    data_dir = pathlib.Path("./smoketest-logs")
    return list(data_dir.glob("*.csv"))


@pytest.mark.bulk
@pytest.mark.parametrize("log_path", get_log_files(), ids=lambda p: p.name)
def test_parser_no_exception(log_path):
    """
    Reads the file as bytes and ensures the parser handles it.
    """
    # 1. Convert filename/path into file_bytes
    file_bytes = log_path.read_bytes()

    # 2. Pass bytes to your library
    try:
        parse_filename_to_session_info(log_path)
        # parser = LogParser(file_bytes)
        # result = parser.parse()
        # assert result is not None
    except Exception as e:
        pytest.fail(f"Parser failed on {log_path.name} with error: {e}")