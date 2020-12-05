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

BR2_EXTERNAL="$(pwd)" make O="$(pwd)/output/$PROJECT" -C "$BUILDROOT_DIR" "$target_defconfig"
make -C "output/$PROJECT" all
