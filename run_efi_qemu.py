#!/usr/bin/env python3
import os 
import sys
import subprocess
import logging
from pathlib import Path

script_dir= Path(__file__).resolve().parent
esp = script_dir/"esp" 
var = script_dir/"qemu"/"vars.fd"   # ovmf vars
code = script_dir/"qemu"/"code.fd"  # ovmf code

def setup_logger(name=__name__,log_level=logging.INFO,log_file=None):
    """
    Terms:
        Logger  记录器：捕获日志时间，但本身并不处理日志的输出
        Handler 处理器：将日志时间发送到不同目的地（控制台、文件等），每个处理器可单独设置日志级别与格式
        Formatter 格式：定义日志记录的输出格式

    Args:
        name: name of logger (module name better)
        log_level: DEBUG/ INFO/ WARNING/ ERROR/ CRITICAL
        log_file: path of log file (optional)
    Returns:
        logger
    """
    # create logger
    # 一个记录器可以有多个处理器，可同时分别输出到不同地方
    # 不同处理器可以设置不同的级别和格式，如控制台输出简洁格式，文件记录详细格式
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # log format("%(module)s")
    log_format = "%(asctime)s|%(levelname)-8s|line %(lineno)d:\t%(message)s"
    
    date_format = "%Y-%m-%d %H:%M:%S"

    # create console handler 
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(log_format,datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    # add to logger
    logger.addHandler(console_handler)

    # optional: file logger 
    if log_file:
        # create log dir automatically
        os.makedirs(os.path.dirname(log_file),exist_ok=True)
        file_handler = logging.FileHandler(log_file,encoding='utf-8')
        file_formatter = logging.Formatter(log_format,datefmt='date_format')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# Initialization Logger
logger = setup_logger(__name__,logging.DEBUG)

""" Logger Basic Config
logging.basicConfig(
    level = logging.INFO,
    format= '%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
"""

"""
    Following is the logic implementation section
"""
def checkfile(esp:Path, code:Path, var:Path):
    esp.exists()
    missing = []
    for f in [esp, code, var]:
        if not f.exists():
            missing.append(str(f))
    if missing:
        logger.error("Missing: %s", ", ".join(missing))
        raise FileNotFoundError("Missing file: " + ", ".join(missing))
    else:
        logger.info("All neccessary files are in place")


def run_qemu():
    command = [
        "sudo","-S", "qemu-system-x86_64",
        "-nodefaults", "-boot", "menu=on,splash-time=0",
        "-machine", "q35", "-smp", "4", "-m", "256M", "-vga", "std",
        "--enable-kvm", "-cpu", "host,vmx=on", "-no-reboot",
        "-fw_cfg", "name=opt/org.tianocore/X-Cpuhp-Bugcheck-Override,string=yes",
        "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04",
        "-drive", f"if=pflash,format=raw,readonly=on,file={code}",
        "-drive", f"if=pflash,format=raw,readonly=on,file={var}",
        "-device", "virtio-scsi-pci", "-device", "virtio-rng-pci",
        "-netdev", "user,id=net0,net=192.168.17.0/24",
        "-device", "virtio-net-pci,netdev=net0,mac=52:54:00:00:00:01",
        "-drive", f"format=raw,file=fat:rw:{esp}"
        ]

    try:
        logger.info("boot qemu")
        logger.debug("\n%s"," ".join(command))

        result = subprocess.run(command)
        if result.returncode ==0 :
            logger.info("qemu quit normally")
            return True
        else:
            logger.error("qemu quit abnormally: %d", result.returncode)
            return False
    except KeyboardInterrupt:
        logger.warning("User Interrupt")
    

def main():
    checkfile(esp,code,var) 
    run_qemu()


if __name__ =="__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("User Interrupt, Program Exit.")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)