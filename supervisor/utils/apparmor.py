"""Some functions around AppArmor profiles."""
import logging
import re

from ..exceptions import AppArmorFileError, AppArmorInvalidError

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_PROFILE = re.compile(r"^profile ([^ ]+).*$")


def get_profile_name(profile_file):
    """Read the profile name from file."""
    profiles = set()

    try:
        with profile_file.open("r") as profile_data:
            for line in profile_data:
                match = RE_PROFILE.match(line)
                if not match:
                    continue
                profiles.add(match.group(1))
    except OSError as err:
        raise AppArmorFileError(
            f"Can't read AppArmor profile: {err}", _LOGGER.error
        ) from err

    if len(profiles) != 1:
        raise AppArmorInvalidError(
            f"To many profiles inside file: {profiles}", _LOGGER.error
        )

    return profiles.pop()


def validate_profile(profile_name, profile_file):
    """Check if profile from file is valid with profile name."""
    if profile_name == get_profile_name(profile_file):
        return True
    return False


def adjust_profile(profile_name, profile_file, profile_new):
    """Fix the profile name."""
    org_profile = get_profile_name(profile_file)
    profile_data = []

    # Process old data
    try:
        with profile_file.open("r") as profile:
            for line in profile:
                match = RE_PROFILE.match(line)
                if not match:
                    profile_data.append(line)
                else:
                    profile_data.append(line.replace(org_profile, profile_name))
    except OSError as err:
        raise AppArmorFileError(
            f"Can't adjust origin profile: {err}", _LOGGER.error
        ) from err

    # Write into new file
    try:
        with profile_new.open("w") as profile:
            profile.writelines(profile_data)
    except OSError as err:
        raise AppArmorFileError(
            f"Can't write new profile: {err}", _LOGGER.error
        ) from err
