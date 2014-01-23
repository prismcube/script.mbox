#!/bin/sh
#
# Author : kos (oskwon@marusys.com), 20130605
#

DEBUG=true
ERROR=true
HDD=false

COMMAND=$1
UPDATE_FILE_NAME=$2
if [ -z $UPDATE_FILE_NAME ]; then
	ERR "Can not found update file."
fi

TOP=
SOURCE=
TARGET=
BLOCKNO=
BOOTCMD=`cat /proc/cmdline`

echo "[*] Update process start!" > /mtmp/update.log

ERR() { if [ $ERROR == true ]; then echo "[!] $1" >> /mtmp/update.log ; fi }
LOG() { if [ $DEBUG == true ]; then echo "[*] $1" >> /mtmp/update.log ; fi }
STATUS() { if [ ! -z $1 ]; then echo "$1" > /mtmp/update.status ; fi }

# function : void rm_image()
# - return : 
rm_image()
{
	if [ -z $TARGET ]; then
		return
	fi
	if [ -e $TARGET/update_ruby ]; then
		rm -Rf $TARGET/update_ruby
		LOG "Removed already exist directory."
	fi
}

# function : void force_exit()
# - return : 
force_exit()
{
	rm_image
	if [ -e /mtmp/force.stop ]; then
		LOG "Remove /mtmp/force.stop"
		rm -f /mtmp/force.stop
	fi
	if [ "$1" == "erase" -a ! -z $BLOCKNO ]; then
		flash_erase /dev/mtd$BLOCKNO 0 0
		LOG "Erase mtdblock [$BLOCKNO]"
	fi
	touch /mtmp/update.stop
	exit 0
}

# function : void startswith(char* data, char* sep)
# - return : echo ("TOKEN")
# - data   :
# - sep    : 
startswith()
{
	STR=$1
	SEP=$2
	END=`echo "$SEP" | wc -c | xargs expr -1 +`
	for TOKEN in $STR ; do
		if [ "${TOKEN:0:$END}" == "$SEP" ]; then
			echo $TOKEN
			break
		fi
	done
}

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

# function : void get_mtdblock_number(char* data, char* sep)
# - return : echo (mtdblock index, error : -1)
# - data   :
# - sep    : 
get_mtdblock_number()
{
	CNT=0
	STR="$1"
	IFS="$2"
	for TOKEN in $STR ; do
		if [ "$(strstr "$TOKEN" "@")" == "TRUE" ]; then
			if [ "$(strstr "$TOKEN" "(update)")" == "TRUE" ]; then
				echo "$CNT"
				IFS=" "
				return
			fi
			CNT=`expr $CNT + 1`
		fi
	done
	IFS=" "
	echo "-1"
}

# function : void check_file(char* path)
# - return : 
# - path   :
check_file()
{
	LOG "Process check md5sum"
	cd $1
	#echo 'cd $1 '$1
	for FILE in `ls -l | grep "^-" | awk '{print $9}'`; do
		check_stop
		#echo 'file '$FILE
		if [ "$(strstr "$FILE" ".md5")" == "FALSE" ]; then
			HASH_SRC=`md5sum $FILE | awk '{print $1}'`
			HASH_DST=`cat $FILE.md5 | awk '{print $1}'`
			#echo 'src hash '$HASH_SRC
			#echo 'dst hash '$HASH_DST
			if [ "$HASH_SRC" == "$HASH_DST" ]; then
				LOG "File is OK : $FILE"
				chmod 775 $FILE
			else
				ERR "Wrong file : $FILE ($HASH_SRC <-> $HASH_DST)"
				force_exit
			fi
		fi
	done
	LOG "Success to check files hash."
	cd -
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
	MOUNT_PATH=$(get_mount_path "/mnt/hdd")
	if [ -z $MOUNT_PATH ]; then
		#MOUNT_PATH=$(get_mount_path "/media/sd")
		#if [ -z $MOUNT_PATH ]; then
		#	ERR "HDD(or USB) was not exist. Please connect HDD(or USB), then retry update."
		#	force_exit
		#fi
		TOP=$MOUNT_PATH
		SOURCE=$UPDATE_FILE_NAME
		TARGET=$TOP
	fi
	if [ -z $TOP ]; then
		TOP=/mnt/hdd0/program
		SOURCE=$UPDATE_FILE_NAME
		TARGET=$TOP/download
		HDD=true
	fi
	cd $TARGET
}

# function : void check_stop()
# - return : 
check_stop()
{
	if [ -e /mtmp/force.stop ]; then 
		force_exit "erase"
	fi
}

# function : void do_start()
# - return : 
do_start()
{
	check_stop
	# find mtdblock number(update).
	MTDPARTS=$(startswith "$BOOTCMD" "mtdparts=")
	BLOCKNO=$(get_mtdblock_number "$MTDPARTS" ",")
	LOG "Found block number(update) : $BLOCKNO"

	check_stop
	# check hdd or usb mount.
	init_path
	LOG "Source : $SOURCE, Target : $TARGET"
	STATUS "5"

	check_stop
	# find update image.
	if [ ! -e $UPDATE_FILE_NAME ]; then
		ERR "Can't found $UPDATE_FILE_NAME"
		force_exit
	fi
	LOG "Check update image file."
	STATUS "10"

	# if already exist, delete directory.
	rm_image

	check_stop
	# unzip update image.
	LOG "Process unzip"
	#cd $SOURCE 
	unzip $UPDATE_FILE_NAME -d $TARGET >> /mtmp/update.log
	LOG "Success unzip"
	STATUS "60"

	check_stop
	# check file md5sum.
	check_file "$TARGET/update_ruby"


	check_stop
	# write image file to nand.
	if [ $HDD == true ]; then
		STATUS "90"
		flash_erase /dev/mtd$BLOCKNO 0 0
		nandwrite -p /dev/mtd$BLOCKNO $TARGET/update_ruby/update.img
		LOG "Success to update image."
	fi
	STATUS "100"
	check_stop
	touch /mtmp/update.complete
	exit 0
}

# function : void do_stop()
# - return : 
do_stop()
{
	MTDPARTS=$(startswith "$BOOTCMD" "mtdparts=")
	BLOCKNO=$(get_mtdblock_number "$MTDPARTS" ",")
	LOG "Found block number(update) : $BLOCKNO"

	init_path
	LOG "Source : $SOURCE, Target : $TARGET"

	touch /mtmp/force.stop
	check_stop
}


case $COMMAND in
	"start") do_start ;;
	"stop") do_stop ;;
	"*") LOG "unknown command option : $COMMAND" ;;
esac




