from functools import cache


@cache
def os_keyring():
    import platform

    """
    Returns an instance of the appropriate keyring backend based on the current operating system.

    This function uses the `platform.system()` function to determine the current operating system and then imports the appropriate keyring backend module. The following keyring backends are supported:
    - Windows: `keyring.backends.Windows.WinVaultKeyring`
    - macOS: `keyring.backends.macOS.Keyring`
    - Linux: `keyring.backends.SecretService.Keyring`

    The function is decorated with `@cache`, which means that the result of the first call to `os_keyring()` is cached and subsequent calls will return the cached result.

    Returns:
        An instance of the appropriate keyring backend.
    """
    if platform.system() == "Windows":
        from keyring.backends.Windows import WinVaultKeyring

        return WinVaultKeyring()
    elif platform.system() == "Darwin":
        from keyring.backends.macOS import Keyring

        return Keyring()
    elif platform.system() == "Linux":
        from keyring.backends.SecretService import Keyring

        return Keyring()


__all__ = ["os_keyring"]
