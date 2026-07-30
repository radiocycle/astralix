import re
import subprocess
import sys

_REQUIREMENTS = re.compile(
    r"^[ \t]*# ?requires:[ \t]*(?P<requirements>[^\r\n]+)[ \t]*$",
    re.MULTILINE,
)


def parse_requirements(source: str) -> list[str]:
    match = _REQUIREMENTS.search(source)
    if not match:
        return []
    return [
        requirement
        for requirement in match.group("requirements").split()
        if not requirement.startswith(("-", "_", "."))
    ]


def build_uv_command(
    requirements: list[str], python: str, system: bool | None = None
) -> list[str]:
    system = sys.prefix == sys.base_prefix if system is None else system
    target = ["--system", "--break-system-packages"] if system else ["--python", python]
    return ["uv", "pip", "install", *target, "--upgrade", *requirements]


def install_requirements(requirements: list[str], python: str = sys.executable) -> None:
    subprocess.run(build_uv_command(requirements, python), check=True)
