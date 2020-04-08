# Cloudflare Warp WireGuard Client
A tool to generate WireGuard profiles for Cloudflare Warp

## Features
- Fetch configuration data from server
- Create new account
- Use existing license key
- Check account type / Warp+ status
- Create WireGuard profile

## Usage
- `poetry install`
- `poetry run python wgcf.py`

Your new account details will be saved under `wgcf-identity.json` and your WireGuard profile under `wgcf-profile.conf`.

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
