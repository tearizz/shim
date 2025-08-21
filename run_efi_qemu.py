#!/usr/bin/env python3
import os 
import sys
import shutil
import subprocess
from pathlib import Path


# efi_src = sys.argv[1]
# efi_file_dir = os.getenv("HOME") + "/codespace/material/efi_file/esp/efi/"
# esp_dir = os.getenv("HOME") + "/codespace/material/efi_file/esp/" 
esp_dir = os.getenv("HOME") + "/codespace/temp/shim/esp/"
ovmf_var = os.getenv("HOME") + "/codespace/material/qemu/ovmf/x64/vars.fd"
ovmf_code = os.getenv("HOME") + "/codespace/material/qemu/ovmf/x64/code.fd"

def main():
    # if sys.argv[1] == "--help" or sys.argv[1] == "-h":
    #     help()
    
    # src,dst = checkfile(efi_src, efi_file_dir)

    # copyfile(src,dst)

    run_qemu()
    # is_file_in_current_dir(sys.argv[1])
    # copyfile(sys.argv[1], "efi_file")
    # copy target file to efi_file 
    # copyfile 
    # run qemu with efi_file 

def checkfile(src,dst):
    if (os.path.exists(efi_src) is False) and os.path.isdir(src):
        print(f"{efi_src} does not exist or is a directory.")
        exit(1) 
    if not os.path.exists(dst):
        print(f"{dst} does not exist.")
        exit(1)
    
    # complete dst path
    if os.path.isdir(dst):
        dest_path = os.path.join(dst, os.path.basename(src))
    else:
        dest_path = dst

    return src,dest_path

def copyfile(src, dst):
    # Previdous code checks if the src exists

    # only check single file now 
    shutil.copy2(src, dst)
    print(f"Copied {src} to {dst}")

def run_qemu():
    command = [
        "sudo",
        "qemu-system-x86_64",
        "-nodefaults",
        "-device", "virtio-rng-pci",
        "-boot", "menu=on,splash-time=0",
        "-machine", "q35",
        "-smp", "4",
        "-m", "256M",
        "-vga", "std",
        "--enable-kvm",
        "-cpu", "host,vmx=on",
        "-no-reboot",
        "-fw_cfg", "name=opt/org.tianocore/X-Cpuhp-Bugcheck-Override,string=yes",
        "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04",
        "-debugcon", "file:./integration-test-debugcon.log",
        "-drive", f"if=pflash,format=raw,readonly=on,file={ovmf_code}",
        "-drive", f"if=pflash,format=raw,readonly=on,file={ovmf_var}",
        "-device", "virtio-scsi-pci",
        "-netdev", "user,id=net0,net=192.168.17.0/24",
        "-device", "virtio-net-pci,netdev=net0,mac=52:54:00:00:00:01",
        "-drive", f"format=raw,file=fat:rw:{esp_dir}"
        ]

    try:  
        result = subprocess.run(
            command,
            check = True,
            text = True,
            capture_output = True)
    except subprocess.CalledProcessError as e:
        print(f"command exec failed: {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
    except Exception as e:
        print(f"exception: {e}")
        exit(1)
    

def help():
    print("Usage: python run_efi_qemu.py <filename>")
    print("This script checks if the specified file exists in the current directory.")
    exit(0)

if __name__ =="__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    else:
        print("Script executed successfully.")
        exit(0)