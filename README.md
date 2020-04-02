# Cloudflare Warp WireGuard Client
A tool to generate WireGuard profiles from a new or existing Cloudflare Warp account

## Features
- Fetch configuration data from server
- Use existing account
- Create new account
- Check account type / Warp+ status
- Create WireGuard profile

## Usage
- `poetry install`
- `poetry run python wgcf.py`

Your new account details will be saved under `wgcf-identity.json` and your WireGuard profile under `wgcf-profile.conf`

## Existing account
Create a new file `wgcf-identity.json` with your account details in the following format:
```json
{
    "account_id": "",
    "access_token": "",
    "private_key": "",
    "license_key": ""
}
```

## Activating WARP+ Unlimited using redeem key
If you don't have `wgcf-identify.json` file yet, run wgcf.py to create a new WARP account.

In 1.1.1.1 app, go to settings > account. Copy the key from there and replace `license_key` value in `wgcf-identify.json` and run wgcf.py.

wgcf.py will automatically update the license key of WARP identity if given `license_key` is differ from registered one  

## Extracting from Android [ROOT ONLY]
- To obtain the `account_id` and `access_token`, you can either:
  - Grab the application's private data and read the shared preferences ([Titanium Backup](https://play.google.com/store/apps/details?id=com.keramidas.TitaniumBackup))
  - OR
  - Sniff the traffic (requires SSL-pinning bypass)
- `private_key` is also stored in the shared preferences. However, it is encrypted with a key stored in the [Android keystore system](https://developer.android.com/training/articles/keystore). You can extract this information directly from the app using [Frida](https://github.com/frida/frida)

Sample scripts can be found in [frida-cloudflare.js](frida-cloudflare.js). Use the magic strings provided in the comments to find the correct symbol names
