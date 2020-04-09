from pathlib import Path
from datetime import datetime, timezone
import requests
import dataclasses
import json
import subprocess
import shutil
import sys
from typing import Optional

api_version = "v0a884"
api = f"https://api.cloudflareclient.com/{api_version}"
reg_url = f"{api}/reg"
status_url = f"{api}/client_config"
terms_of_service_url = "https://www.cloudflare.com/application/terms/"

data_path = Path(".")
identity_path = data_path.joinpath("wgcf-identity.json")
config_path = data_path.joinpath("wgcf-profile.conf")

default_headers = {"Accept-Encoding": "gzip",
                   "User-Agent": "okhttp/3.12.1"}

# toggle to allow sniffing traffic
debug = False


def get_verify() -> bool:
    return not debug


def get_config_url(account_id: str) -> str:
    return f"{reg_url}/{account_id}"


def get_account_url(account_id: str) -> str:
    return f"{get_config_url(account_id)}/account"


def get_devices_url(account_id: str) -> str:
    return f"{get_account_url(account_id)}/devices"


def get_account_reg_url(account_id: str, device_token: str) -> str:
    return f"{get_account_url(account_id)}/reg/{device_token}"


@dataclasses.dataclass
class AccountData:
    account_id: str
    access_token: str
    private_key: str
    license_key: str


@dataclasses.dataclass
class ConfigurationData:
    local_address_ipv4: str
    local_address_ipv6: str
    endpoint_address_host: str
    endpoint_address_ipv4: str
    endpoint_address_ipv6: str
    endpoint_public_key: str
    warp_enabled: bool
    account_type: str
    warp_plus_enabled: bool
    license_key_updated: bool


def get_timestamp() -> str:
    # SimpleDateFormat("yyyy-MM-dd\'T\'HH:mm:ss", Locale.US)
    timestamp = datetime.now(tz=timezone.utc).astimezone(None).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    # trim microseconds to 2 digits
    timestamp = timestamp[:-10] + timestamp[-6:]
    # separate timezone offset
    timestamp = timestamp[:-2] + ":" + timestamp[-2:]
    return timestamp


def gen_private_key() -> str:
    result: str = subprocess.run(["wg", "genkey"], capture_output=True).stdout.decode('utf-8')
    return result.strip()


def gen_public_key(private_key: str) -> str:
    result: str = subprocess.run(["wg", "pubkey"], input=bytes(private_key, 'utf-8'),
                                 capture_output=True).stdout.decode('utf-8')
    return result.strip()


def do_register() -> AccountData:
    timestamp = get_timestamp()
    private_key = gen_private_key()
    public_key = gen_public_key(private_key)
    data = {"install_id": "", "tos": timestamp, "key": public_key, "fcm_token": "", "type": "Android",
            "model": "PC", "locale": "en_US"}

    headers = default_headers.copy()
    headers["Content-Type"] = "application/json; charset=UTF-8"

    response = requests.post(reg_url, json=data, headers=headers, verify=get_verify())

    response.raise_for_status()
    response = json.loads(response.content)
    return AccountData(response["id"], response["token"], private_key, response["account"]["license"])


def save_identitiy(account_data: AccountData):
    with open(identity_path, "w") as f:
        f.write(json.dumps(dataclasses.asdict(account_data), indent=4))


def load_identity() -> AccountData:
    with open(identity_path, "r") as f:
        account_data = AccountData(**json.loads(f.read()))
        return account_data


def enable_warp(account_data: AccountData):
    data = {"warp_enabled": True}

    headers = default_headers.copy()
    headers["Authorization"] = f"Bearer {account_data.access_token}"
    headers["Content-Type"] = "application/json; charset=UTF-8"

    response = requests.patch(get_config_url(account_data.account_id), json=data, headers=headers, verify=get_verify())

    response.raise_for_status()
    response = json.loads(response.content)
    assert response["warp_enabled"] is True


def get_server_conf(account_data: AccountData) -> ConfigurationData:
    headers = default_headers.copy()
    headers["Authorization"] = f"Bearer {account_data.access_token}"

    response = requests.get(get_config_url(account_data.account_id), headers=headers, verify=get_verify())

    response.raise_for_status()
    response = json.loads(response.content)

    addresses = response["config"]["interface"]["addresses"]
    peer = response["config"]["peers"][0]
    endpoint = peer["endpoint"]

    account = response["account"] if "account" in response else ""
    account_type = account["account_type"] if account != "" else "free"
    warp_plus = account["warp_plus"] if account != "" else False
    license_key_updated = response["account"]["license"].strip() != account_data.license_key.strip()

    return ConfigurationData(addresses["v4"], addresses["v6"], endpoint["host"], endpoint["v4"],
                             endpoint["v6"], peer["public_key"], response["warp_enabled"],
                             account_type, warp_plus, license_key_updated)


def update_license_key(account_data: AccountData, conf_data: ConfigurationData) -> bool:
    if conf_data.account_type == "free" and account_data.license_key != "":
        headers = default_headers.copy()
        headers["Authorization"] = f"Bearer {account_data.access_token}"
        data = {"license": account_data.license_key}

        url = get_account_url(account_data.account_id)
        activation_resp = requests.put(url, json=data, headers=headers, verify=get_verify())
        activation_resp.raise_for_status()
        activation_resp = json.loads(activation_resp.content)

        return activation_resp["warp_plus"]
    elif conf_data.account_type == "unlimited":
        # already has unlimited subscription
        return True

    return False


def get_device_active(account_data: AccountData) -> Optional[bool]:
    headers = default_headers.copy()
    headers["Authorization"] = f"Bearer {account_data.access_token}"

    url = get_devices_url(account_data.account_id)
    activation_resp = requests.get(url, headers=headers, verify=get_verify())
    activation_resp.raise_for_status()
    activation_resp = json.loads(activation_resp.content)

    my_device = next((x for x in activation_resp if x["id"] == account_data.account_id), None)
    return None if my_device is None else my_device["active"]


def set_device_active(account_data: AccountData, status: bool) -> bool:
    headers = default_headers.copy()
    headers["Authorization"] = f"Bearer {account_data.access_token}"
    data = {"active": status}

    url = get_account_reg_url(account_data.account_id, account_data.account_id)
    activation_resp = requests.patch(url, json=data, headers=headers, verify=get_verify())
    activation_resp.raise_for_status()
    activation_resp = json.loads(activation_resp.content)

    my_device = next(x for x in activation_resp if x["id"] == account_data.account_id)
    return my_device["active"]


def get_wireguard_conf(private_key: str, address_1: str, address_2: str, public_key: str, endpoint: str) -> str:
    return f"""
[Interface]
PrivateKey = {private_key}
DNS = 1.1.1.1
Address = {address_1}
Address = {address_2}

[Peer]
PublicKey = {public_key}
AllowedIPs = 0.0.0.0/0
AllowedIPs = ::/0
Endpoint = {endpoint}
"""[1:-1]


def create_conf(account_data: AccountData, conf_data: ConfigurationData):
    with open(config_path, "w") as f:
        f.write(
            get_wireguard_conf(account_data.private_key, conf_data.local_address_ipv4,
                               conf_data.local_address_ipv6, conf_data.endpoint_public_key,
                               conf_data.endpoint_address_host))


if __name__ == "__main__":
    if shutil.which("wg") is None:
        print("Error: 'wg' must be installed and added to PATH")
        print("More information: https://www.wireguard.com/install/")
        sys.exit(1)

    data_path.mkdir(exist_ok=True)
    account_data: AccountData

    if not identity_path.exists():
        print("This project is in no way affiliated with Cloudflare!")
        print(f"Cloudflare's Terms of Service: {terms_of_service_url}")
        if not input("Do you agree? (y/N): ").lower() == "y":
            sys.exit(2)

        print(f"Creating new identity...")
        account_data = do_register()
        save_identitiy(account_data)
    else:
        print(f"Loading existing identity...")
        account_data = load_identity()

    print(f"Getting configuration...")
    conf_data = get_server_conf(account_data)

    if conf_data.license_key_updated:
        print("Updating account license key...")
        result = update_license_key(account_data, conf_data)
        if result:
            conf_data = get_server_conf(account_data)

    device_status = get_device_active(account_data)
    if device_status is None:
        print("This device not registered to the account!")
        sys.exit(3)

    if conf_data.warp_plus_enabled and not device_status:
        print("This device is registered to the account, but not activated. It is highly recommended to activate it "
              "before using Warp+.")
        if input("Would you like to activate this device? (y/N): ").lower() == "y":
            device_status = set_device_active(account_data, True)

    if not conf_data.warp_enabled:
        print(f"Enabling Warp...")
        enable_warp(account_data)
        conf_data.warp_enabled = True

    print(f"Warp+ enabled: {conf_data.warp_plus_enabled}")
    print(f"Device activated: {device_status}")

    print(f"Account type: {conf_data.account_type}")
    print(f"Warp+ enabled: {conf_data.warp_plus_enabled}")

    print("Creating WireGuard configuration...")
    create_conf(account_data, conf_data)

    print("All done! Find your files here:")
    print(identity_path.absolute())
    print(config_path.absolute())
