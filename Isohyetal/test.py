import subprocess

# Credentials
nas_username = 'wfs'
nas_password = 'wwff55!@#'
nas_local_dir = '/mnt/nas'
nas_remote_path = 'wd.s.dstor.pagasa.local/wfs/Isohyetal'  # Use 'r' to handle backslashes
source_image_dir = '/home/CollabPy/Isohyetal/isohyet_images/20181022.png'

def mount_network_server(nas_remote_path, nas_local_dir):
    try:
        # Use subprocess to run the mount command with sudo
        subprocess.run(['sudo', 'mount', '-t', 'cifs', f'//{nas_remote_path}', nas_local_dir,
                        '-o', f'username={nas_username},password={nas_password}'])
        print(f"Successfully mounted {nas_remote_path} to {nas_local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error mounting {nas_remote_path} to {nas_local_dir}: {e}")

def transfer_to_nas(source_image_dir, nas_local_dir):
    try:
        # Use subprocess to copy the file to the NAS directory with sudo
        subprocess.run(['sudo', 'cp', source_image_dir, nas_local_dir])
        print(f"Successfully transferred {source_image_dir} to {nas_local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error transferring {source_image_dir} to {nas_local_dir}: {e}")

# Mount the network server
mount_network_server(nas_remote_path, nas_local_dir)

# Transfer the source image to the NAS local directory
transfer_to_nas(source_image_dir, nas_local_dir)
