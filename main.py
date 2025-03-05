import csv
from json import JSONDecodeError

import requests
from rich import print

USE_PROXY = False
BASE_URL = f"https://zpi.zerion.io/wallet/get-meta/v1"


def get_data(address, proxy):
    resp = requests.get(
        f"{BASE_URL}?identifiers={address}",
        proxies={"http": proxy, "https": proxy},
        headers={
            "content-type": "application/json",
            "zerion-client-type": "web",
            "zerion-client-version": "1.144.1",
        },
    )

    try:
        return resp.json()["data"][0]["membership"]
    except JSONDecodeError:
        print(f"Invalid JSON response for identifier: {address}")


def write_to_csv(addres, level, xp_earned, xp_to_claim):
    with open("zerion_xp.csv", "a", newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(["Wallet", "Level", "XP earned", "XP to claim"])

        writer.writerow([addres, level, xp_earned, xp_to_claim])


def output_data(data, address, _id):
    level, xp_earned = data["level"], data["xp"]["earned"]

    if data["retro"] is None:
        xp_to_claim = 0
    else:
        zerion_xp = data["retro"]["zerion"]["total"]
        global_xp = data["retro"]["global"]["total"]
        xp_to_claim = zerion_xp + global_xp

    print(f"{_id} {address} | Lvl {level} | XP earned {xp_earned:>5} | XP to claim: {xp_to_claim}")  # fmt: skip
    write_to_csv(address, level, xp_earned, xp_to_claim)


def main():
    with open("addresses.txt") as file:
        addresses = [row.strip() for row in file]

    with open("proxies.txt") as file:
        proxies = [f"http://{row.strip()}" for row in file]

    for index, address in enumerate(addresses, start=1):
        proxy = proxies[index % len(proxies)] if USE_PROXY else None
        _id = f"[{index:02}/{len(addresses)}]"

        data = get_data(address, proxy)
        output_data(data, address, _id)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelled by user")
    except Exception as err:
        print(f"An error occured: {err}")
