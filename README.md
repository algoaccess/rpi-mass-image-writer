# rpi-mass-image-writer
Raspberry Pi that writes to many USB drives at one go.

![Screen](/photos/front-idle-with-case.jpg)

Everything in with a nice 3D printed case.

![Screen](/photos/front-writing-no-case.jpg)

The innards

#How to use?
1. Login to shared folder
2. Transfer image files via samba to shared folder
3. Plug in all USB flash drives to write to
4. Hit left button to enumerate all images and drives 
5. Use up/down buttons to select image
6. Press the right button to start writing to drives. You can press it again to terminate writing.
7. Press the select button (extreme left) to shutdown device properly to prevent data corruption. The words "Shutting down" will remain even after the device has completely shutdown, so just wait for the activity light to turn off before pulling the power.

#Hardware
1. Raspberry Pi 2 Model B (Others will work just as fine)
2. Adafruit i2c 16x2 LCD Pi Plate with keypad
3. USB hubs (not all hubs are supported well, use the ones from this [list](http://elinux.org/RPi_Powered_USB_Hubs))
4. USB SD card adapters
5. USB Gigabit adapter (optional)

#Setting up

I use Arch Linux as it is stripped down and boots up far faster than Raspbian. With some modifications to the setup instructions, you can run this on Raspbian as well.

##Installing packages and configuring i2C

```bash
pacman -Syu python2 i2c-tools samba pv git

modprobe i2c-dev
echo "i2c-dev" > /etc/modules-load.d/i2c-dev.conf
```

On the latest versions of Arch Linux, it seems the i2c bus is disabled by default. We have to enable it. [Source](http://archlinuxarm.org/forum/viewtopic.php?f=31&t=8330)

```bash
nano /boot/config.txt

#Add the following lines
device_tree=bcm2709-rpi-2-b.dtb  #Replace this line with "bcm2708-rpi-b.dtb" or "bcm2708-rpi-b-plus.dtb" depending on your Raspberry Pi type.
device_tree_param=i2c1=on
device_tree_param=spi=on

reboot
```

##Clone this repo and run the app

```bash
git clone https://github.com/algoaccess/rpi-mass-image-writer.git
cd rpi-mass-image-writer
python2 writer.py
```
The LCD screen should now turn on.

##Setting up samba 

The folder we are sharing is the images directory.

```bash
nano /etc/samba/smb.conf
#Add/Modify the following lines to your smb.conf file between #start and #end
#Start
[global]
workgroup = WORKGROUP
server string = SD Duplicator
security = user
log file = /var/log/samba/%m.log
max log size = 50
dns proxy = no

[images]
path = /root/rpi-mass-image-writer/images
writable = yes
#End


#Create a user for samba
smbpasswd -a root
systemctl enable smbd
```

##Using a separate USB Gigabit adapter

Transfering large image files takes a long time on the internal 10/100 adapter so I opted to use a Gigabit adapter instead. Note that Pi is using USB2.0 with other devices sharing the bus so the speed up just about 2x which is pretty good.

```bash
cp /etc/netctl/examples/ethernet-dhcp /etc/netctl/eth1
nano /etc/netctl/eth1

#Change the "Interface" value from eth0 to eth1

netctl enable eth1
reboot
#Test the network connection
```

##Starting on boot

```bash
cp /root/rpi-mass-image-writer/writer.service /etc/systemd/system/
systemctl enable writer.service
reboot
```

#References
1. [Open Source Image Duplicator](https://github.com/rockandscissor/osid)
2. [Adafruit Char Plate LCD](https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/overview)
3. [i2c setup on Arch Linux](http://cfedk.host.cs.st-andrews.ac.uk/site/?q=2013-pi)
4. [Rpi 2 Model B 3D case top](http://www.thingiverse.com/thing:588608)
5. [Rpi 2 Model B 3D case bottom](http://www.thingiverse.com/thing:582366)
6. [Enable i2c on Arch Linux](http://archlinuxarm.org/forum/viewtopic.php?f=31&t=8330)
7. [dd to multiple drives](https://joshhead.wordpress.com/2011/08/04/multiple-output-files-with-dd-utility/)
