# TF2 Sentry Quickstart Instructions
Download Raspbian (Lite): https://www.raspberrypi.org/downloads/raspbian/
Download Etcher for writing the Raspian image to a micro sd card. 8GB should be sufficient size: https://www.balena.io/etcher/
After Etcher finishes, pull out the sd card and re-insert.
Edit **/Volumes/boot/wpa_supplicant.conf** (on a Mac) and put this:
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
network={
  ssid="«your_SSID»"
  psk="«your_PSK»"
  key_mgmt=WPA-PSK
}
```
And to enable ssh, to this:
```
cd /Volumes/boot
touch ssh
cd ~
```
Eject the sd card, put the sd card in Raspberry Pi, and boot.
Find ip for the new Raspberry Pi:
```
sudo nmap -sS -p 22 10.0.0.0/24
```
And ssh to it:
```
ssh pi@[ip]
```
The default password is `raspberry`. Change it once logged in:
```
passwd
```
  
Install a bunch of stuff:
```
sudo apt-get install git
sudo apt-get install python3-pip
sudo apt-get install vim
sudo pip3 update
```

Install Blynk Server. The Python code will connect to this server, and so will the ios client. You can skip this step if you're running a Blynk server elsewhere or if you want to use Blynk cloud:
```
sudo apt-get install oracle-java8-jdk
cd ~
mkdir Blynk
cd Blynk
wget "https://github.com/blynkkk/blynk-server/releases/download/v0.39.12/server-0.39.12-java8.jar"
crontab -e
```
Add the following line to the crontab:
```
> @reboot java -jar /home/pi/Blynk/server-0.39.12-java8.jar -dataFolder /home/pi/Blynk/data -serverConfig /home/pi/Blynk/server.properties &
```
Edit Blynk server properties:
```
vi /home/pi/Blynk/server.properties
```
And put the following:
```
server.ssl.key.pass=<PW>
admin.email=<EMAIL>
admin.pass=<PW>
server.host=0.0.0.0
```

Open firewall:
```
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 9443
sudo iptables -t nat -A PREROUTING -p tcp --dport 8441 -j REDIRECT --to-port 9443
sudo apt-get install iptables-persistent
sudo iptables -t nat -A PREROUTING -p tcp --dport 8442 -j REDIRECT --to-port 8080
sudo -i
iptables-save > /etc/iptables/rules.v4
exit
```

Add sound libraries:
```
sudo apt-get install python-pygame
```
Edit /usr/share/alsa/alsa.conf and change these 0's to 1's:
```
defaults.ctl.card 0
defaults.pcm.card 0
```
Start Blynk Server. This is a one time action - normally it'll start on boot:
```
java -jar /home/pi/Blynk/server-0.39.12-java8.jar -dataFolder /home/pi/Blynk/data -serverConfig /home/pi/Blynk/server.properties &
```
  
Admin panel can be reached at https://your_ip:9443/admin

Get TF2 code:
```
git clone git@github.com:martaaay/tf2sentry.git
cd tf2sentry
sudo pip install -r requirements.txt
python main.py
```
  
Download the Blynk app. Hit login and choose the weird button at the bottom for connecting to LAN. Set this to your raspberry pi IP.

The auth token will have to be placed in main.py.

(This part of the documentation may need to be fleshed out more. I dont think the Blynk control panel is encoded anywhere in the code)
