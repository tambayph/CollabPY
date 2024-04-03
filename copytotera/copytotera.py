import subprocess
import os

# Credentials
nas_username = 'wfs'
nas_password = 'wwff55!@#'
nas_local_dir = '/mnt/nas'

def mount_network_server(nas_remote_path, nas_local_dir):
    # Check if the directory is already mounted
    is_mounted = os.path.ismount(nas_local_dir)

    if is_mounted:
        # Unmount the directory
        subprocess.run(['sudo', 'umount', '-f', nas_local_dir])
        print(f"Unmounted {nas_local_dir}")

    try:
        # Use subprocess to run the mount command with sudo
        subprocess.run(['sudo', 'mount', '-t', 'cifs', f'//{nas_remote_path}', nas_local_dir,
                        '-o', f'username={nas_username},password={nas_password}'])
        print(f"Successfully mounted {nas_remote_path} to {nas_local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error mounting: {e}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")

def transfer_to_nas(source_image_dir, nas_local_dir):
    try:
        # Check if nas_local_dir exists and is a directory
        if not os.path.isdir(nas_local_dir):
            # If nas_local_dir is not a directory, create it
            subprocess.run(['sudo', 'mkdir', '-p', nas_local_dir])
        # Use subprocess to copy the file to the NAS directory with sudo
        subprocess.run(['sudo', 'cp', source_image_dir, nas_local_dir])
        print(f"Successfully transferred {source_image_dir} to {nas_local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error transferring {source_image_dir} to {nas_local_dir}: {e}")

# # Mount the network server
# mount_network_server(nas_remote_path, nas_local_dir)

# # Transfer the source image to the NAS local directory
# transfer_to_nas(source_image_dir, nas_local_dir)
