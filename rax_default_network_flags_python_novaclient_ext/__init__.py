# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Instance create default networks extension
"""
import argparse

from novaclient.v1_1.shell import _boot
from novaclient.v1_1.shell import _find_flavor
from novaclient.v1_1.shell import _find_image
from novaclient.v1_1.shell import _poll_for_status
from novaclient import utils


@utils.arg('--flavor',
     default=None,
     metavar='<flavor>',
     help="Flavor ID (see 'nova flavor-list').")
@utils.arg('--image',
     default=None,
     metavar='<image>',
     help="Image ID (see 'nova image-list'). ")
@utils.arg('--meta',
     metavar="<key=value>",
     action='append',
     default=[],
     help="Record arbitrary key/value metadata to /meta.js "\
          "on the new server. Can be specified multiple times.")
@utils.arg('--file',
     metavar="<dst-path=src-path>",
     action='append',
     dest='files',
     default=[],
     help="Store arbitrary files from <src-path> locally to <dst-path> "\
          "on the new server. You may store up to 5 files.")
@utils.arg('--key-name',
    metavar='<key-name>',
    help="Key name of keypair that should be created earlier with \
        the command keypair-add")
@utils.arg('--key_name',
    help=argparse.SUPPRESS)
@utils.arg('name', metavar='<name>', help='Name for the new server')
@utils.arg('--user-data',
    default=None,
    metavar='<user-data>',
    help="user data file to pass to be exposed by the metadata server.")
@utils.arg('--user_data',
    help=argparse.SUPPRESS)
@utils.arg('--availability-zone',
    default=None,
    metavar='<availability-zone>',
    help="The availability zone for instance placement.")
@utils.arg('--availability_zone',
    help=argparse.SUPPRESS)
@utils.arg('--security-groups',
    default=None,
    metavar='<security-groups>',
    help="Comma separated list of security group names.")
@utils.arg('--security_groups',
    help=argparse.SUPPRESS)
@utils.arg('--block-device-mapping',
    metavar="<dev-name=mapping>",
    action='append',
    default=[],
    help="Block device mapping in the format "
        "<dev-name>=<id>:<type>:<size(GB)>:<delete-on-terminate>.")
@utils.arg('--block_device_mapping',
    action='append',
    help=argparse.SUPPRESS)
@utils.arg('--hint',
        action='append',
        dest='scheduler_hints',
        default=[],
        metavar='<key=value>',
        help="Send arbitrary key/value pairs to the scheduler for custom use.")
@utils.arg('--nic',
     metavar="<net-id=net-uuid,v4-fixed-ip=ip-addr>",
     action='append',
     dest='nics',
     default=[],
     help="Create a NIC on the server.\n"
           "Specify option multiple times to create multiple NICs.\n"
           "net-id: attach NIC to network with this UUID (optional)\n"
           "v4-fixed-ip: IPv4 fixed address for NIC (optional).\n"
           "port-id: attach NIC to port with this UUID (optional)")
@utils.arg('--config-drive',
     metavar="<value>",
     dest='config_drive',
     default=False,
     help="Enable config drive")
@utils.arg('--poll',
    dest='poll',
    action="store_true",
    default=False,
    help='Blocks while instance builds so progress can be reported.')
@utils.arg('--no-public',
    dest='public',
    action='store_false',
    default=True,
    help='Boot instance without public network connectivity.')
@utils.arg('--no-service-net',
    dest='service_net',
    action='store_false',
    default=True,
    help='Boot instance without service network connectivity.')
def do_boot(cs, args):
    """Boot a new server."""
    boot_args, boot_kwargs = _boot(cs, args)

    extra_boot_kwargs = utils.get_resource_manager_extra_kwargs(do_boot, args)
    boot_kwargs.update(extra_boot_kwargs)

    nics = []
    if args.public:
        nics.append({'net-id': '00000000-0000-0000-0000-000000000000',
                     'v4-fixed-ip': '', 'port-id': ''})
    if args.service_net:
        nics.append({'net-id': '11111111-1111-1111-1111-111111111111',
                     'v4-fixed-ip': '', 'port-id': ''})
    if 'nics' in boot_kwargs:
        boot_kwargs['nics'].extend(nics)
    else:
        boot_kwargs['nics'] = nics

    server = cs.servers.create(*boot_args, **boot_kwargs)

    # Keep any information (like adminPass) returned by create
    info = server._info
    server = cs.servers.get(info['id'])
    info.update(server._info)

    flavor = info.get('flavor', {})
    flavor_id = flavor.get('id', '')
    info['flavor'] = _find_flavor(cs, flavor_id).name

    image = info.get('image', {})
    image_id = image.get('id', '')
    info['image'] = _find_image(cs, image_id).name

    info.pop('links', None)
    info.pop('addresses', None)

    utils.print_dict(info)

    if args.poll:
        _poll_for_status(cs.servers.get, info['id'], 'building', ['active'])
