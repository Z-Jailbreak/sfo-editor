import subprocess

MAX_TITLE = 71
MAX_DESC = 128


def apply_changes(sfo_command, sfo_path, title, description):

    commands = []

    if title:
        commands.append(["maintitle", title])
    if description:
        commands.append(["subtitle", description])

    if not commands:
        return "empty"

    if not sfo_command or not sfo_path:
        return "error"

    for key, value in commands:
        try:
            result = subprocess.run(
                [sfo_command, "-e", key, value, sfo_path],
                capture_output=True,
            )
        except OSError:
            return "error"

        if result.returncode != 0:
            return "error"

    return "ok"


def query_value(sfo_command, sfo_path, key):

    if not sfo_command or not sfo_path:
        return ""

    try:
        result = subprocess.run(
            [sfo_command, "-q", key, sfo_path],
            capture_output=True,
        )
    except OSError:
        return ""

    if result.returncode != 0:
        return ""

    return result.stdout.decode("utf-8", errors="replace").strip()
