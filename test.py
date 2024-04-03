#!/usr/bin/env python3

import os
import subprocess

def mount_nas(username, password, domain, local_dir, remote_path):
    # Check if the local directory exists
    if not os.path.exists(local_dir):
        # Create the local directory (mount point)
        subprocess.run(['sudo', 'mkdir', local_dir])

    # Mount the NAS share
    mount_command = [
        'sudo', 'mount.cifs',
        f'//{remote_path}', local_dir,
        '-o', f'username={username},password={password},domain={domain}'
    ]
    subprocess.run(mount_command)

def transfer_files_to_nas(local_dir, source_dir, extension):
    # Fetch all files in the source directory with the specified extension
    files_to_copy = [f for f in os.listdir(source_dir) if f.endswith(f'.{extension}')]

    # Transfer each file to the NAS using cp
    for file_to_copy in files_to_copy:
        subprocess.run(['sudo', 'cp', os.path.join(source_dir, file_to_copy), f'{local_dir}/'])

def unmount_nas(local_dir):
    # Check if the directory is currently mounted
    if os.path.ismount(local_dir):
        # Unmount the NAS share
        subprocess.run(['sudo', 'umount', local_dir])
    else:
        print(f"The directory {local_dir} is not currently mounted.")

if __name__ == "__main__":
    # Specify your NAS credentials and paths
    nas_username = 'wfs'
    nas_password = 'wwff55!@#'
    nas_domain = 'WFS'
    nas_local_dir = '/mnt/nas'
    nas_remote_path = 'dstor3.wd.pagasa.local/wfs-pf/Tests'

    # Specify the source directory and file extension
    source_image_dir = '/home/CollabPy/Isohyetal/isohyet_images'
    file_extension = 'png'

    # Mount the NAS share if the directory doesn't exist
    if not os.path.exists(nas_local_dir):
        mount_nas(nas_username, nas_password, nas_domain, nas_local_dir, nas_remote_path)

    # Transfer all files with .png extension from the source directory to the NAS using cp
    transfer_files_to_nas(nas_local_dir, source_image_dir, file_extension)

    # Unmount the NAS share when done
    unmount_nas(nas_local_dir)

