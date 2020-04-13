# Cloudflare Warp WireGuard Client
A tool to generate WireGuard profiles for Cloudflare Warp

> ## :warning: Notice:
> ## This project has been deprecated in favor of [wgcf](https://github.com/ViRb3/wgcf) - a complete re-write in Golang. It includes numerous new features and improvements, runs natively on any operating system, and has zero dependencies. [Get wgcf now!](https://github.com/ViRb3/wgcf)

## Features
- Fetch configuration data from server
- Create new account
- Use existing license key
- Check account type / Warp+ status
- Create WireGuard profile

## Usage
1. Install [WireGuard](https://www.wireguard.com/install/). Make sure its command-line tool `wg` is accessible from your `PATH`
1. Install [Python 3.7+](https://www.python.org/downloads/)
2. Install [poetry](https://github.com/python-poetry/poetry) using [pip](https://pypi.org/project/pip/):
    ```bash
    pip3 install poetry
    ```
3. Download [this project](https://github.com/ViRb3/cloudflare-warp-wireguard-client/archive/master.zip) and extract it
4. Open a shell in the extracted directory
5. _(only first time)_ Install the dependencies:
    ```bash
    poetry install
    ```
6. Run the script:
    ```bash
    poetry run python wgcf.py
    ```

Your new account details will be saved under `wgcf-identity.json` and your WireGuard profile under `wgcf-profile.conf`.

You can use the WireGuard profile on any OS that supports WireGuard, including Windows, macOS, Linux and Android. For more information, please refer to the [WireGuard installation instructions](https://www.wireguard.com/install/).

## Using existing license key
If you have an existing account, for an example on your phone, you can use its license key to bind this device's account to that of your phone and share its Warp+ features. Please note that there is a limit of a maximum of 5 active linked devices.

1. Make sure you have ran this script at least once to create an identity
2. Once you have the `wgcf-identity.json` file, open it in your favorite text editor and replace the `license_key` value with the license key of your other device
3. When you re-run this script, it will detect the change and automatically update your account

### Android
To see your account's license key on Android:
1. Open the `1.1.1.1` app
2. Click on the hamburger menu button in the top-right corner
3. Navigate to: `Account` > `Key`
