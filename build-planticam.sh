#!/bin/bash

PROJECT="planticam"
target_defconfig="$PROJECT"_defconfig

if [ "$BUILDROOT_DIR" = "" ] ; then
	if [ ! -d ../buildroot ] ; then
		echo 'Make sure to have unpacked buildroot in ../buildroot or set environment variable BUILDROOT_DIR'
		exit 1
	else
		BUILDROOT_DIR=../buildroot
	fi
fi

if [ "$1" = "clean" ] ; then
	echo "Cleaning up"
	rm -rf output/planticam/target
	rm -rf output/planticam/build/planticam*
	rm -rf output/planticam/per-package/planticam*
fi

BR2_EXTERNAL="$(pwd)" make O="$(pwd)/output/$PROJECT" -C "$BUILDROOT_DIR" "$target_defconfig"
make -C "output/$PROJECT" all
