#!/bin/bash

BLOCK_DEVICE="/dev/mmcblk0"

echo "Creating partition..."
sudo fdisk $BLOCK_DEVICE <<EOF
n
p
3


t
3
0c
w
EOF

echo "Formatting partition..."
sudo mkfs.vfat ${BLOCK_DEVICE}p3
