
ROOT_DIR=`pwd`
RTL_SDR_REPO="git://git.osmocom.org/rtl-sdr.git"
SOAPY_SDR_REPO="https://github.com/pothosware/SoapySDR.git"
LIQUID_DSP_REPO="https://github.com/jgaeddert/liquid-dsp"
WX_WIDGETS_REPO="https://github.com/wxWidgets/wxWidgets/releases/download/v3.1.0/wxWidgets-3.1.0.tar.bz2"
WX_WIDGETS_DIR="$ROOT_DIR/wxWidgets-staticlib"
CUBIC_SDR_REPO="https://github.com/cjcliffe/CubicSDR/releases/tag/0.2.4"
SOAPY_RTL_SDR_REPO="https://github.com/pothosware/SoapyRTLSDR.git"

CMAKE_ATOMIC_FIX='SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -latomic")'

########################################################################
#
# Get prerequisite libraries and software
#
########################################################################

sudo apt update -y
sudo apt upgrade -y

sudo apt install -y git build-essential automake cmake
sudo apt install -y libpulse-dev libgtk-3-dev
sudo apt install -y freeglut3 freeglut3-dev
sudo apt install -y libjpeg-dev libtiff-dev libsdl1.2-dev
sudo apt install -y libgstreamer-plugins-base0.10-dev
sudo apt install -y libgstreamer-plugins-base1.0-dev
sudo apt install -y libnotify-dev freeglut3 freeglut3-dev libsm-dev
sudo apt install -y libwebkitgtk-dev libwebkitgtk-3.0-dev libwebkit2gtk-4.0-dev
sudo apt install -y libxtst-dev git-core libusb-1.0-0-dev
sudo apt install -y libasound-dev libpulse-dev gnuradio gnuradio-dev
sudo apt install -y libhamlib2 libhamlib-utils libhamlib++-dev
sudo apt install -y libhamlib-dev libhamlib-doc python-libhamlib2

########################################################################
#
# Disable DVB drivers for RTL chip
#
########################################################################
cd $ROOT_DIR
cat <<EOF >no-rtl.conf
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
EOF

sudo mv no-rtl.conf /etc/modprobe.d/



########################################################################
#
# Get and build RTL-SDR driver
#
########################################################################
cd $ROOT_DIR
git clone $RTL_SDR_REPO
cd rtl-sdr
mkdir build & cd build
cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON
make
sudo make install
sudo ldconfig
cd $ROOT_DIR
sudo cp ./rtl-sdr/rtl-sdr.rules /etc/udev/rules.d/


########################################################################
#
# Get and build SoapySDR
#
########################################################################
cd $ROOT_DIR
git clone $SOAPY_SDR_REPO
cd SoapySDR
echo -e "$CMAKE_ATOMIC_FIX\n$(cat CMakeLists.txt)" > CMakeLists.txt
mkdir build && cd build
cmake ../ -DCMAKE_BUILD_TYPE=Release
make -j4
sudo make install
sudo ldconfig
SoapySDRUtil --info #test SoapySDR install


########################################################################
#
# Get and build LiquidDSP
#
########################################################################
cd $ROOT_DIR
git clone $LIQUID_DSP_REPO
cd liquid-dsp
./bootstrap.sh
./configure --enable-fftoverride 
make -j4
sudo make install
sudo ldconfig


########################################################################
#
# Get and build wxWidgets
#
########################################################################
cd $ROOT_DIR
wget $WX_WIDGETS_REPO
tar -xvjf wxWidgets-3.1.0.tar.bz2  
cd wxWidgets-3.1.0/
mkdir -p $WX_WIDGETS_DIR
./autogen.sh 
./configure --with-opengl --disable-shared --enable-monolithic --with-libjpeg --with-libtiff --with-libpng --with-zlib --disable-sdltest --enable-unicode --enable-display --enable-propgrid --disable-webkit --disable-webview --disable-webviewwebkit --prefix=`echo $WX_WIDGETS_DIR` CXXFLAGS="-std=c++0x" --with-libiconv=/usr
make -j4
sudo make install

########################################################################
#
# Get and build CubicSDR
#
########################################################################
cd $ROOT_DIR
git clone $CUBIC_SDR_REPO
cd CubicSDR
echo -e "$CMAKE_ATOMIC_FIX\n$(cat CMakeLists.txt)" > CMakeLists.txt
mkdir build && cd build
cmake ../ -DUSE_HAMLIB=0 -DCMAKE_BUILD_TYPE=Release -DwxWidgets_CONFIG_EXECUTABLE=$WX_WIDGETS_DIR/bin/wx-config
make
cd x86/
./CubicSDR
sudo make install

########################################################################
#
# Get and build Soapy RTL SDR driver
#
########################################################################
git clone $SOAPY_RTL_SDR_REPO
cd SoapyRTLSDR
echo -e "$CMAKE_ATOMIC_FIX\n$(cat CMakeLists.txt)" > CMakeLists.txt
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make
sudo make install
sudo ldconfig
SoapySDRUtil --probe     
