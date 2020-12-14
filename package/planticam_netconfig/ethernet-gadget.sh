#!/bin/bash
cd /sys/kernel/config/usb_gadget/
mkdir -p pizero
cd pizero

# usb descriptor
echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0200 > bcdUSB # USB2
echo 0x02 > bDeviceClass
echo 0x00 > bDeviceSubClass
echo 0x3066 > bcdDevice

# windows extensions
echo 1 >os_desc/use
echo 0xcd > os_desc/b_vendor_code
echo "MSFT100" > os_desc/qw_sign

# echo 0x01 > bDeviceProtocol
mkdir -p strings/0x409
echo "fedcba9876543211" > strings/0x409/serialnumber
echo "Dunkelstern" > strings/0x409/manufacturer
echo "Planticam USB Device" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# functions
mkdir -p functions/rndis.usb0
echo "RNDIS" > functions/rndis.usb0/os_desc/interface.rndis/compatible_id
echo "5162001" > functions/rndis.usb0/os_desc/interface.rndis/sub_compatible_id

HOST="00:dc:c8:f7:75:14" # "HostPC"
SELF="00:dd:dc:eb:6d:a1" # "BadUSB"
echo $HOST > functions/rndis.usb0/host_addr
echo $SELF > functions/rndis.usb0/dev_addr

ln -s functions/rndis.usb0 configs/c.1

ln -s configs/c.1 os_desc

echo "20980000.usb" > UDC

udevadm settle -t 5 || :
ls /sys/class/udc > UDC
ifup usb0

