#!/bin/env python3
#
# Reads the output of $(cargo metadata) from standard input and copies the assets as specified in the deb section
# to the specified <destination>.
#
# Usage: cargo metadata --format-version 1 | copy_assety.py <package-name> <destination>
#
# Options:
#   package-name: As present in $(cargo metadata)
#   destination: The root of the folder where the assets are copied. This directory will be created if
#                it doesn't exist already.
#  
import sys
import json
import shutil
import os
import os.path


def assets(package_name, cargo_metadata): 
    for package in filter(lambda cargo_package: cargo_package['name'] == package_name, cargo_metadata['packages']):
        return package['metadata']['deb']['assets']


def copy_assets(root, assets):
    """
    assets is a list of lists. Each enclosed list has three elements: (source, destination_folder, destination_file_mod)

    Example json:
          "assets": [
            [
              "../target/release/stackable-zookeeper-operator-server",
              "opt/stackable/zookeeper-operator/",
              "755"
            ],
            [
              "../deploy/crd/zookeepercluster.crd.yaml",
              "etc/stackable/zookeeper-operator/crd/",
              "644"
            ],
            [
              "../deploy/config-spec/properties.yaml",
              "etc/stackable/zookeeper-operator/config-spec/",
              "644"
            ]
          ]
    """
    for asset_def in assets:
        source = asset_def[0][3:] ### remove the leading ../
        dest = asset_def[1]
        dest_mod = int(asset_def[2], 8)
        
        ### build the destination file name
        absolute_dest = os.path.join(root, dest, os.path.basename(source))
        ### create destination directory if doesn't exist already
        os.makedirs(os.path.dirname(absolute_dest), mode=0o755, exist_ok=True)
        print("Copying {} to {}".format(source, absolute_dest))
        shutil.copyfile(source, absolute_dest)
        os.chmod(absolute_dest, dest_mod)


def main(args):
    if len(args) != 3:
        raise ValueError("Usage: copy_assets.py <package-name> <destination>")

    package_name = args[1]
    destination = args[2]

    if not os.path.isdir(destination):
        raise ValueError("Destination is not a directory: {}".format(destination))

    cargo_deb_metadata = json.load(sys.stdin)
    cargo_deb_assets = assets(package_name, cargo_deb_metadata)
    copy_assets(destination, cargo_deb_assets)


if __name__ == '__main__':
    main(sys.argv)
