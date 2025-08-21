- fork from [shim: shim-15.5 branch](https://github.com/rhboot/shim)

- thanks for [AdjWang](https://github.com/AdjWang)

- add http request in UEFI Shell 

- add & modify: 
    - add: `shim-src/http-request.c`, 
    - modity: `shim-src/httpboot.c`,`shim-src/include/httpboot.h`,`shim-src/Makefile`


- fix `BdsDxe: failed to load Boot0001 "UEFI QEMU HARDDISK QM00001"...` WAIT TOO LONG
    - add `NvVars` to esp dir

- script:
    - `python3 run_efi_qemu.py esp/efi/http-request.efi`