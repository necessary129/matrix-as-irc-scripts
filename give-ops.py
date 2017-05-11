#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.parse as urllib

import requests
import yaml


def get_appservice_token(reg):
    with open(reg, "r") as f:
        reg_yaml = yaml.load(f)
        return reg_yaml["as_token"]


def get_room_id(hs_url, alias, token):
    res = requests.get(hs_url + "/_matrix/client/r0/directory/room/" + urllib.quote(alias) +
                       "?access_token=" + token).json()
    return res.get("room_id", None)


def get_power_level(hs_url, room_id, token):
    return requests.get(hs_url + "/_matrix/client/r0/rooms/" + urllib.quote(room_id) +
                        "/state/m.room.power_levels?access_token=" + token).json()


def put_power_level(hs_url, room_id, token, event):
    res = requests.put(
        hs_url + "/_matrix/client/r0/rooms/" + urllib.quote(room_id) + "/state/m.room.power_levels?access_token=" +
        token, data=json.dumps(event),
    )
    res.raise_for_status()


def main(registration, homeserver, user_id, alias):
    print("Granting ops to %s in %s" % (user_id, alias))
    token = get_appservice_token(registration)
    if not token:
        raise Exception("Cannot read as_token from registration file")
    room_id = get_room_id(homeserver, alias, token)
    if not room_id:
        raise Exception("Cannot resolve room alias to room_id")
    power_level_event = get_power_level(homeserver, room_id, token)
    print("Modifying existing power level event:")
    print(json.dumps(power_level_event))
    current_power_level = power_level_event['users'].get(user_id, 0)
    if current_power_level != 50:
        cont = input("Current user is not an op. Countinue? [y/n]: ")
        if cont.lower() == 'y':
            pass
        else:
            return
    power_level_event["users"][user_id] = 100
    put_power_level(homeserver, room_id, token, power_level_event)
    print("Granted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Grant full ops to a user in a portal room")
    parser.add_argument("-r", "--registration", help="The path to the AS registration file",
                        default="/etc/matrix-synapse/appservice.reg.yaml")
    parser.add_argument("-i", "--userid", help="The user ID to grant ops to eg '@matthew:matrix.org'", required=True)
    parser.add_argument("-a", "--alias", help="The alias of the portal room eg '#freenode_#matrix-dev:matrix.org'",
                        required=True)
    parser.add_argument("-s", "--homeserver", help="Base homeserver URL eg 'https://matrix.org'",
                        default="https://diasp.in")
    args = parser.parse_args()
    if not args.userid or not args.alias or not args.registration or not args.homeserver:
        parser.print_help()
        sys.exit(1)
    main(registration=args.registration, user_id=args.userid, alias=args.alias, homeserver=args.homeserver)
