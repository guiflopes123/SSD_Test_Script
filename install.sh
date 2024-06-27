#

if [ -s /etc/redhat-release ]; then
    # fedora, centos7
    sudo yum install -y make redhat-rpm-config python3-devel python3-pip python3-tkinter
elif [ -f /etc/debian_version ]; then
    # ubuntu
    sudo apt install -y python3-setuptools python3-dev python3-pip python3-tk
elif [ -f /etc/SUSE-brand ]; then
    # SUSE
    sudo zypper install -y python3-setuptools python3-devel python3-pip python3-tk
elif [ -f /etc/arch-release ]; then
    # ArchLinux
    sudo pacman -S python3-setuptools python3-devel python3-pip tk
else
    echo "unknown system type."
    exit 1
fi

# get depended source code and software teste

sudo python3 -m pip install --upgrade pip
sudo apt install nvme-cli
sudo pip install -U google-generativeai --break-system-packages
sudo rm /usr/lib/python3.*/EXTERNALLY-MANAGED
sudo apt-get install python-pip
sudo pip install numpy
sudo pip install pandas
echo "nvme_ID install done."
