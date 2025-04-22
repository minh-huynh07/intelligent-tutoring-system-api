from flask import Blueprint, redirect, request, session, url_for
import requests
import re

from api.steam_service import steam_bp

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

def extract_steam_id(claimed_id_url: str) -> str:
    match = re.search(r"https://steamcommunity.com/openid/id/(\d+)", claimed_id_url)
    return match.group(1) if match else None

@steam_bp.route('/steam')
def steam_login():
    openid_params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": url_for('steam_service.steam_authorize', _external=True),
        "openid.realm": request.host_url,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }

    query_string = '&'.join([f"{k}={v}" for k, v in openid_params.items()])
    return redirect(f"{STEAM_OPENID_URL}?{query_string}")

@steam_bp.route('/steam/authorize')
def steam_authorize():
    params = request.args.to_dict()
    post_data = params.copy()
    post_data["openid.mode"] = "check_authentication"

    response = requests.post(STEAM_OPENID_URL, data=post_data)
    if "is_valid:true" in response.text:
        steamid64 = extract_steam_id(params.get("openid.claimed_id", ""))
        if not steamid64:
            return redirect("http://localhost:3000/login-failed")

        account_id = int(steamid64) - 76561197960265728
        return redirect(f"http://localhost:3000/login-success?steamid={steamid64}&account_id={account_id}")

    return redirect("http://localhost:3000/login-failed")
