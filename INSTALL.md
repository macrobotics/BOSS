# INSTALL.md
## Arduino
First update Apt:

	sudo apt-get update && sudo apt-get upgrade

Then install Arduino:

	sudo apt-get install arduino
	
## Python
First update Apt:

	sudo apt-get update && sudo apt-get upgrade

Then install python and libraries:

	sudo apt-get install python

## OpenCV
### Dependencies
First install this first set of dependecies:

	sudo apt-get -y install build-essential cmake cmake-qt-gui
	pkg-config libpng12-0 libpng12-dev libpng++-dev libpng3
	libpnglite-dev zlib1g-dbg zlib1g zlib1g-dev pngtools libtiff4-dev libtiff4
	libtiffxx0c2 libtiff-tools
	
Then install this second set of dependencies:

	sudo apt-get -y install libjpeg8 libjpeg8-dev libjpeg8-dbg
	libjpeg-progs ffmpeg libavcodec-dev libavcodec53 libavformat53
	libavformat-dev libgstreamer0.10-0-dbg libgstreamer0.10-0
	libgstreamer0.10-dev libxine1-ffmpeg libxine-dev libxine1-bin
	libunicap2 libunicap2-dev libdc1394-22-dev libdc1394-22
	libdc1394-utils swig libv4l-0 libv4l-dev python-numpy libpython2.6
	python-dev python2.6-dev libgtk2.0-dev pkg-config

### Build Source
Then get the source and build from source:

	wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.3/OpenCV-2.4.3.tar.bz2
	tar -xvjpf OpenCV-2.4.3.tar.bz2
	cd OpenCV-2.4.3/ && mkdir build && cd build
	
Now you can build the source (warning, will take a LONG TIME on the RaspberryPi)

	cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON ..
	make
	sudo make install

### Configuration
Open the OpenCV configuration file:

	sudo nano /etc/ld.so.conf.d/opencv.conf
	
Add the following line:

	/usr/local/lib
	
Open Bash configuration file:

	sudo nano /etc/bash.bashrc
	
Add the following lines:

	PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig
	export PKG_CONFIG_PATH

