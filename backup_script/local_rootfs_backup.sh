#!/bin/sh

export LANG=$1
export HARDDISK=0


########################## DECLARATION OF VARIABLES ###########################
START=$(date +%s)
DATE=`date +%Y%m%d_%H%M`
IMAGEVERSION=`date +%Y%m%d`
MKFS=/usr/sbin/mkfs.ubifs
NANDDUMP=/usr/sbin/nanddump
UBINIZE=/usr/sbin/ubinize
WORKDIR=$1
UBINIZE_ARGS="-m 2048 -p 128KiB"


###################### DEFINE CLEAN-UP ROUTINE ################################
clean_up()
{
umount /tmp/bi/root > /dev/null 2>&1
rmdir /tmp/bi/root > /dev/null 2>&1
rmdir /tmp/bi > /dev/null 2>&1
rm -rf "$WORKDIR" > /dev/null 2>&1
}

###################### BIG OOPS!, HOLY SH... (SHELL SCRIPT :-))################
big_fail()
{
	clean_up
	echo "big_fail()"
	exit 0
}
##### I QUIT #####


################### START THE LOGFILE /tmp/BackupSuite.log ####################
echo "Backup stick found" > /tmp/BackupSuite.log
echo "Starting backup process" >> /tmp/BackupSuite.log
echo "Backup date_time  = $DATE" >> /tmp/BackupSuite.log
echo "Working directory  = $WORKDIR" >> /tmp/BackupSuite.log

######################### TESTING FOR UBIFS AND JFFS2 ##########################
if grep rootfs /proc/mounts | grep ubifs > /dev/null; then	
	ROOTFSTYPE=ubifs
else
	echo "JFFS2 NOT SUPPORTED ANYMORE"
	big_fail
fi

####### TESTING IF ALL THE TOOLS FOR THE BUILDING PROCESS ARE PRESENT #########
if [ ! -f $NANDDUMP ] ; then
	echo -n "$NANDDUMP " ; echo "nanddump not found."
	echo "NO NANDDUMP FOUND, ABORTING" >> /tmp/BackupSuite.log
	big_fail
fi
if [ ! -f $MKFS ] ; then
	echo -n "$MKFS " ; echo "mkfs.ubifs not found."
	echo "NO MKFS.UBIFS FOUND, ABORTING" >> /tmp/BackupSuite.log
	big_fail
fi
if [ ! -f $UBINIZE ] ; then
	echo -n "$UBINIZE " ; echo "ubinize not found."
	echo "NO UBINIZE FOUND, ABORTING" >> /tmp/BackupSuite.log
	big_fail
fi

########## TESTING WHICH BRAND AND MODEL SATELLITE RECEIVER IS USED ###########

MKUBIFS_ARGS="-m 2048 -e 126976 -c 4000"
#MAINDEST="$MEDIA/fullbackup/$DATE/prismcube/"
#EXTRA="$MEDIA/prismcube"
#echo "Destination        = $MAINDEST" >> /tmp/BackupSuite.log

############# START TO SHOW SOME INFORMATION ABOUT BRAND & MODEL ##############

echo "BACKUP TOOL FOR MAKING A COMPLETE BACKUP"
echo
echo
echo "Please wait... This will take a while"
echo " "

#exit 0  #USE FOR DEBUGGING/TESTING


##################### PREPARING THE BUILDING ENVIRONMENT ######################
#rm -rf "$WORKDIR"		# GETTING RID OF THE OLD REMAINS IF ANY
#echo "Remove directory   = $WORKDIR" >> /tmp/BackupSuite.log
mkdir -p "$WORKDIR"		# MAKING THE WORKING FOLDER WHERE EVERYTHING HAPPENS
echo "Recreated directory = $WORKDIR" >> /tmp/BackupSuite.log
mkdir -p /tmp/bi/root
echo "Created directory   = /tmp/bi/root" >> /tmp/BackupSuite.log
sync
mount --bind / /tmp/bi/root




#backup loader, u-boot, kernel, checkusb.img file
echo "Starting loader and kernel bakcup" >> /tmp/BackupSuite.log
BOOT_DIR=/boot
#if [ -f $BOOT_DIR/uldr.bin ] && [ -f $BOOT_DIR/u-boot.bin ] && [ -f $BOOT_DIR/kernel.uImage ] && [ -f $BOOT_DIR/checkusb.img ] ; then
if [ -f $BOOT_DIR/uldr.bin ] && [ -f $BOOT_DIR/u-boot.bin ] && [ -f $BOOT_DIR/kernel.uImage ] && [ -f $BOOT_DIR/checkusb.img ] && [ -f $BOOT_DIR/ramdisk_update_script.sh] ; then
	cp $BOOT_DIR/* $WORKDIR/
else
	echo "Backup files not found" >> /tmp/BackupSuite.log
	big_fail
fi

#backup uImage, ramdisk
$NANDDUMP /dev/mtd6 -q > $WORKDIR/uImage
$NANDDUMP /dev/mtd7 -q > $WORKDIR/ramdisk.gz

####################### START THE REAL BACK-UP PROCESS ########################
#------------------------------------------------------------------------------
############################# MAKING UBINIZE.CFG ##############################
echo \[ubifs\] > "$WORKDIR/ubinize.cfg"
echo mode=ubi >> "$WORKDIR/ubinize.cfg"
echo image="$WORKDIR/root.ubi" >> "$WORKDIR/ubinize.cfg"
echo vol_id=0 >> "$WORKDIR/ubinize.cfg"
echo vol_type=dynamic >> "$WORKDIR/ubinize.cfg"
echo vol_name=rootfs >> "$WORKDIR/ubinize.cfg"
echo vol_flags=autoresize >> "$WORKDIR/ubinize.cfg"
echo " " >> /tmp/BackupSuite.log
echo "UBINIZE.CFG CREATED WITH THE CONTENT:"  >> /tmp/BackupSuite.log
cat "$WORKDIR/ubinize.cfg"  >> /tmp/BackupSuite.log
touch "$WORKDIR/root.ubi"
chmod 644 "$WORKDIR/root.ubi"
echo "--------------------------" >> /tmp/BackupSuite.log

#############################  MAKING ROOT.UBI(FS) ############################
echo "Creating rootfs.rootfs.ubi"
echo "Please wait... This will take a while" >> /tmp/BackupSuite.log

$MKFS -r /tmp/bi/root -o "$WORKDIR/root.ubi" $MKUBIFS_ARGS
if [ -f "$WORKDIR/root.ubi" ] ; then
	echo "ROOT.UBI MADE:" >> /tmp/BackupSuite.log
	ls -e1 "$WORKDIR/root.ubi" >> /tmp/BackupSuite.log
else 
	echo "$WORKDIR/root.ubi NOT FOUND"  >> /tmp/BackupSuite.log
	big_fail
fi

$UBINIZE -o "$WORKDIR/rootfs.rootfs.ubi" $UBINIZE_ARGS "$WORKDIR/ubinize.cfg" >/dev/null
chmod 644 "$WORKDIR/rootfs.rootfs.ubi"

#delete ubi files
rm $WORKDIR/root.ubi $WORKDIR/ubinize.cfg

if [ -f "$WORKDIR/rootfs.rootfs.ubi" ] ; then
	echo "ROOT.UBIFS MADE:" >> /tmp/BackupSuite.log
	ls -e1 "$WORKDIR/rootfs.rootfs.ubi" >> /tmp/BackupSuite.log
else 
	echo "$WORKDIR/rootfs.rootfs.ubi NOT FOUND"  >> /tmp/BackupSuite.log
	big_fail
fi

echo "Making md5sum..." >> /tmp/BackupSuite.log
if [ -f $WORKDIR/checkusb.img ]; then
		md5sum $WORKDIR/checkusb.img > $WORKDIR/checkusb.img.md5
fi
if [ -f $WORKDIR/ramdisk_update_script.sh ]; then
		md5sum $WORKDIR/ramdisk_update_script.sh > $WORKDIR/ramdisk_update_script.sh.md5
fi
if [ -f $WORKDIR/kernel.uImage ]; then
		md5sum $WORKDIR/kernel.uImage > $WORKDIR/kernel.uImage.md5
fi
if [ -f $WORKDIR/u-boot.bin ]; then
 		md5sum $WORKDIR/u-boot.bin > $WORKDIR/u-boot.bin.md5
fi
if [ -f $WORKDIR/uldr.bin ]; then
		md5sum $WORKDIR/uldr.bin > $WORKDIR/uldr.bin.md5
fi
if [ -f $WORKDIR/rootfs.rootfs.ubi ]; then
		md5sum $WORKDIR/rootfs.rootfs.ubi > $WORKDIR/rootfs.rootfs.ubi.md5
fi

#Success backup, so umount and remove directories.
umount /tmp/bi/root > /dev/null 2>&1
rmdir /tmp/bi/root > /dev/null 2>&1
rmdir /tmp/bi > /dev/null 2>&1

echo "Making md5sum done" >> /tmp/BackupSuite.log
echo "Userdata backup done" >> /tmp/BackupSuite.log
echo "File system backup done" >> /tmp/BackupSuite.log
echo "Done" >> /tmp/BackupSuite.log
sleep 3
exit 0
