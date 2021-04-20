#!/usr/bin/bash

export BUILD_PATH=$PWD

export PGPLOT_DIR=$BUILD_PATH/lib/pgplot
export FFTW_LIB=$BUILD_PATH/lib/fftw-3.3.9/gcc-pure
export TEMPO=$BUILD_PATH/lib/tempo
export CFITSIO=$BUILD_PATH/lib/cfitsio
export PRESTO=$BUILD_PATH/presto-3.0.1
export C_INCLUDE_PATH=$PRESTO/include:$FFTW_LIB/include:$CFITSIO/include:$C_INCLUDE_PATH
export LD_LIBRARY_PATH=$FFTW_LIB/lib:$CFITSIO/lib:$PRESTO/lib:$PGPLOT_DIR:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$CFITSIO/lib/pkgconfig:$FFTW_LIB/lib/pkgconfig:$PKG_CONFIG_PATH

export PATH=$PATH:$PRESTO/bin:$TEMPO/src

#cd $PRESTO/FAST
#(time python ./multi_pipeline.py J0631+4147_tracking_0001.fits) > log.`now` 2>&1

#cd $PRESTO/FAST_FIL
#(time python ./multi_pipeline.py J0631+4147_tracking_0001.fil) > log.`now` 2>&1

#cd $PRESTO/FAST_FIL
#(time python ./time_pipeline.py J0631+4147_tracking_0001.fil) > log.`now` 2>&1

# cd $PRESTO/FAST_ALL
# (time python ./time_pipeline.py J0631+4147_tracking_all.fits) > log.serial 2>&1


#echo `pwd`
#echo "start run GBT"
#cd $PRESTO/TestData1
#(time python ./pipeline.py GBT_Lband_PSR.fil) > log 2>&1
#echo "finish run GBT"
#
cd $PRESTO/TestData2
#echo `pwd`
#echo "start run Dec"
(time python ./pipeline.py Dec+1554_arcdrift+23.4-M12_0194.fil) > log.$NOW_TIME 2>&1
#echo "finish run Dec"
#
#cd $PRESTO/FAST
#echo `pwd`
#echo "start run FAST"
#(time python ./time_pipeline.py J0631+4147_tracking_0001.fits) > log.`now` 2>&1
#echo "finish run FAST"

