#!/usr/bin/env python3

import argparse
import urllib.parse as urllib

import requests
import yaml


def get_room_id(hs_url, alias, token):
    res = requests.get(hs_url + "/_matrix/client/r0/directory/room/" + urllib.quote(alias) +
                       "?access_token=" + token).json()
    return res.get("room_id", None)


def get_reg_info(reg, option):
    with open(reg, "r") as f:
        reg_yaml = yaml.load(f)
        return reg_yaml[option]


def get_appservice_token(reg):
    return get_reg_info(reg, "as_token")


def link(hs_url, as_url, as_token, irc_server, channel, room_alias, op_nick, matrix_user, channel_key=None):
    room_id = get_room_id(hs_url, room_alias, as_token)
    d = {
        "remote_room_server": irc_server,
        "remote_room_channel": channel,
        "matrix_room_id": room_id,
        "op_nick": op_nick,
        "user_id": matrix_user,
    }
    if channel_key:
        d['key'] = channel_key
    res = requests.post(as_url + "/_matrix/provision/link", json=d).json()
    return res


def unlink(hs_url, as_url, as_token, irc_server, channel, room_alias, matrix_user, channel_key=None):
    room_id = get_room_id(hs_url, room_alias, as_token)
    d = {
        "remote_room_server": irc_server,
        "remote_room_channel": channel,
        "matrix_room_id": room_id,
        "user_id": matrix_user,
    }
    if channel_key:
        d['key'] = channel_key
    res = requests.post(as_url + "/_matrix/provision/unlink", json=d).json()
    return res


def main():
    parser = argparse.ArgumentParser("Link or unlink matrix rooms to IRC")
    parser.add_argument("-r", "--registration", help="The path to the AS registration file",
                        default="/etc/matrix-synapse/appservice.reg.yaml")
    parser.add_argument("-i", "--userid", help="The user ID requesting the bridge eg: '@noteness:matrix.org",
                        required=True)
    parser.add_argument("-a", "--alias", help="The alias of the matrix room eg: '#diaspin:diasp.in'",
                        required=True)
    parser.add_argument("-e", "--homeserver", help="Base homeserver URL eg 'https://matrix.org'",
                        default="https://diasp.in")
    parser.add_argument("-s", "--ircserver", help="IRC server to bridge to", default="irc.piratpartiet.se")
    parser.add_argument("-c", "--channel", help="IRC channel to bridge to", required=True)
    parser.add_argument("-o", "--op", help="Nick of the op in channel.", required=True)
    parser.add_argument("-k", "--key", help="Channel key", required=False)
    parser.add_argument("-u", '--unlink', help="Unlink instead of linking", action="store_true")
    args = parser.parse_args()
    hs_url = args.homeserver
    reg = args.registration
    as_url = get_reg_info(reg, "url")
    as_token = get_appservice_token(reg)
    irc_server = args.ircserver
    channel = args.channel
    op = args.op
    userid = args.userid
    key = args.key
    alias = args.alias
    print("Linking {} to {}:{}".format(alias, irc_server, channel))
    if args.unlink:
        print(
            unlink(hs_url, as_url, as_token, irc_server, channel, alias, userid, key)
        )
    else:
        print(
            link(hs_url, as_url, as_token, irc_server, channel, alias, op, userid, key)
        )


if __name__ == "__main__":
    main()
