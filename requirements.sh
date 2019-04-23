#!/usr/bin/env bash
#
# This script is used to install required software depedencies for Marriott example applciation
#

echo "updating software repository..."
sudo apt-get update

# install zip
sudo apt install -y zip

if [ $1='broker' ]; then
    echo "starting preparing MQTT Broker server..."
    sudo apt-get install -y mosquitto
    sleep 0.3
    sudo systemctl start mosquitto
elif [ $1='manager' ]; then
    CHECK_PYTHON3=$(which python3)
    CHECK_PIP3=$(which pip3)

    # Python3 is typically pre-installed on Ubuntu 18.04
    if [ $CHECK_PYTHON3='' ]; then
        echo "Python3 is not available."
        echo "Installing Python3 and pip3..."
        sudo apt-get install -y python3
        sudo apt-get install -y python3-pip
    fi

    # Install pip3
    if [ $CHECK_PIP3='' ]; then
        echo "Installing pip3..."
        sudo apt-get install -y python3-pip
    fi

    echo "start installing required python libraries..."

    # Install python libraries using pip
    echo -e "The following libraries will be installed: \n paho-mqtt \n Flask \n boto3 \n string \n pycryptodome"

    sudo pip3 install paho-mqtt Flask boto3 pycryptodome simplejson pycryptodomex

    # Install aws cli
    echo "Start install aws cli..."
    sudo pip3 install awscli --upgrade --user

    # Check whether aws config file is available
    # this directory is typically available on EC2 instance

    if ls ~/.aws/; then
        echo -e "awscli is available, if you want to update aws credential, please run: \n aws configure"
    else
        echo "installing aws cli"
        sudo pip3 install awscli --upgrade --user
    fi
fi