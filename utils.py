def check_afm(afm: str) -> bool:
    """
    Checks the integrity of a Greek tax number (ΑΦΜ): nine digits, the last of which is a check digit.

    Check-digit algorithm adapted from code by marmako@gmail.com.
    """
    if not isinstance(afm, str) or not afm.isdigit() or len(afm) != 9:
        return False
    if afm == "000000000":
        return False

    weights = [256, 128, 64, 32, 16, 8, 4, 2]
    total = sum(int(digit) * weight for digit, weight in zip(afm[:8], weights))
    return (total % 11) % 10 == int(afm[8])
