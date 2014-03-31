#!/bin/bash
VolumeName="RamCache"
SizeInMB=521
NumSectors=$((2*1024*SizeInMB))
DeviceName=`hdid -nomount ram://$NumSectors`

echo $DeviceName
 
diskutil eraseVolume HFS+ RAMDisk $DeviceName