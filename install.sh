#!/bin/bash

if ! command -v wget &> /dev/null; then
    echo "wget not found. Installing..."

    if [ -f "/etc/debian_version" ]; then  # Debian
        sudo apt-get update
        sudo apt-get install -y wget
        sudo apt-get install openssl
    elif [ -f "/etc/centos-release" ]; then  # CentOS
        sudo yum update
        sudo yum install -y wget
        sudo yum update openssl
    elif [ -f "/etc/lsb-release" ]; then  # Ubuntu
        sudo apt-get update
        sudo apt-get install -y wget
        sudo apt-get install openssl
    else
        echo -e "\033[31mError: This version is not currently supported, only Centos, Ubuntu, and Debian versions are supported\033[0m"
        exit 1
    fi
fi


install_dir=$(pwd)/python-3.9.7


if [ -d "$install_dir" ]; then
    echo "Installation directory $install_dir already exists. Skipping installation."
else
    echo "Installing Python 3.9.7..."

    echo "Downloading Python 3.9.7 source code..."
    wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz || {
        echo -e "\033[31mError: Failed to download Python source code. Please check your network or other settings.\033[0m"

        exit 1
    }

    echo "Extracting source code..."
    tar -xvf Python-3.9.7.tgz || {
        echo -e "\033[31mError: Failed to decompress Python source code, please try again\033[0m"
        rm -f Python-3.9.7.tgz
        exit 1
    }

    cd Python-3.9.7

    echo "Configuring..."
    ./configure --prefix=$install_dir || {
        echo -e "\033[31mError: Configure failed.\033[0m"
        exit 1
    }

    echo "Compiling and installing..."
    make && make install || {
        echo -e "\033[31mError: Compilation or installation failed.\033[0m"
        exit 1
    }

    cd ..
    rm -rf Python-3.9.7 Python-3.9.7.tgz

    echo -e "\033[32;1mPython 3.9.7 installed in $install_dir\033[0m"
fi

# 使用刚刚安装的Python来运行项目依赖安装
echo "Installing project dependencies using Python 3.9.7..."
$install_dir/bin/python3.9 -m pip install -r requirements.txt

echo "Project dependencies installed."

echo -e "\033[32;1mPackage manifest generated successfully. \033[0m"
echo
echo -e "\033[32;1m前台运行：$install_dir/bin/python3.9 Bot.py \033[0m"
echo -e "\033[32;1m后台运行：nohup $install_dir/bin/python3.9 Bot.py &\033[0m"