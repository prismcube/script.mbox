#!/bin/sh

COMMAND=$1

# function : void strstr(char* data, char* sep)
# - return : echo ("TRUE" | "FALSE")
# - data   :
# - sep    : 
strstr()
{
	RET="TRUE"
	if [ -z `echo "$1" | grep "$2"` ]; then
		RET="FALSE"
	fi
	echo $RET
}

# function : void get_mount_path(char* type)
# - return : echo ("MOUNT PATH")
# - type   : usb, hdd.....
get_mount_path()
{
	for POINT in `mount | awk '{print $3}'`; do
		if [ "$(strstr "$POINT" "$1")" == "TRUE" ]; then
			echo $POINT
			return
		fi
	done
}

# function : void init_path()
# - return : 
init_path()
{
	MOUNT_PATH=$(get_mount_path "/media/sda2")
	if [ ! -z $MOUNT_PATH ]; then
		MOUNT_PATH=$(get_mount_path "/media/sda5")
		if [ ! -z $MOUNT_PATH ]; then
			MOUNT_PATH=$(get_mount_path "/media/sda3")
			if [ ! -z $MOUNT_PATH ]; then
				HDD=true
			else
				HDD=false
			fi
		else
			HDD=false
		fi
	else
		HDD=false
	fi

	if [ $HDD == true ]; then
		TOP=$(get_mount_path "media/sdb")
		XBMC_SOURCE=$(get_mount_path "media/sdb")/update_ruby/xbmc_data
		XBMC_TARGET=$(get_mount_path "/media/sda3")/.xbmc
		CONFIG_SOURCE=$(get_mount_path "media/sdb")/update_ruby/config_data
		CONFIG_TARGET=/root/config/

	else
		TOP=$(get_mount_path "media/sda")
		XBMC_SOURCE=$(get_mount_path "media/sda")/update_ruby/xbmc_data
		XBMC_TARGET=/root/mnt/hdd0/program/.xbmc/addons
		CONFIG_SOURCE=$(get_mount_path "media/sda")/update_ruby/config_data
		CONFIG_TARGET=/root/config/
	fi

	echo "xbmc source $XBMC_SOURCE"
	echo "xbmc target $XBMC_TARGET"
	echo "config source $CONFIG_SOURCE"
	echo "config target $CONFIG_TARGET"
}

# function : void mount_ubifs()
# - return : 
mount_ubifs()
{
	ubiattach /dev/ubi_ctrl -m 4 -d 0
	mkdir /root
	mount -t ubifs /dev/ubi0_0 /root -o sync
	
	ubiattach /dev/ubi_ctrl -m 2 -d 1
	mkdir /root/config
	mount -t ubifs /dev/ubi1_0 /root/config -o sync
}
# function : void check_custom_shell()
restore()
{

# check restort shell
	if [ -d $XBMC_SOURCE ]; then
		echo "xbmc backup data found. start restore"
		cp $XBMC_SOURCE/* $XBMC_TARGET/ -a
	fi
	if [ -d $CONFIG_SOURCE ]; then
		echo "config backup data found. start restore"
		cp $CONFIG_SOURCE/* $CONFIG_SOURCE/ -a
	fi
}


# function : void do_start()
# - return : 
do_start()
{
	init_path
	echo "init_patch done"
	mount_ubifs
	echo "config, rootfs mount done"
	restore
	sync
}

do_start


