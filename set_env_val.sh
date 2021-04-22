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

