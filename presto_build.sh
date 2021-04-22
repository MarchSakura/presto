#!/usr/bin/bash

export BUILD_PATH=$PWD

FCC=gfortran
F77=gfortran
CC=gcc

export FFTW_INSTALL=$BUILD_PATH/src/fftw-3.3.9
export FFTW=$BUILD_PATH/lib/fftw-3.3.9/gcc-pure
export PGPLOT=$BUILD_PATH/lib/pgplot
export TEMPO=$BUILD_PATH/lib/tempo
export CFITSIO_INSTALL=$BUILD_PATH/src/cfitsio-3.49
export CFITSIO=$BUILD_PATH/lib/cfitsio

# tar xzvf $BUILD_PATH/download/v3.0.1.tar.gz -C .
export PRESTO=$BUILD_PATH/presto-3.0.1
export C_INCLUDE_PATH=$PRESTO/include:$FFTW/include:$CFITSIO/include:$C_INCLUDE_PATH
export LD_LIBRARY_PATH=$FFTW/lib:$CFITSIO/lib:$PRESTO/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$CFITSIO/lib/pkgconfig:$FFTW/lib/pkgconfig:$PKG_CONFIG_PATH
export PGPLOT_DIR=$PGPLOT
export FFTW_LIB=$FFTW/lib

cd $PRESTO/src
sed -i '\%pkg-config --cflags%s/pkg-config/PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 pkg-config/' Makefile
sed -i '\%pkg-config --libs%s/pkg-config/PKG_CONFIG_ALLOW_SYSTEM_LIBS=1 pkg-config/' Makefile
make clean
make makewisdom
make

echo -e "\033[41;36m presto source make finish. \033[0m"

cd $PRESTO/python/presto
sed -i '\%from presto%s/from presto //' filterbank.py
sed -i '\%from presto%s/from presto\./from /' sigproc.py
sed -i '\%from presto%s/from presto //' psrfits.py
cd $PRESTO
sed -i '\%\["cpgplot"%s/\["cpgplot"/\["gfortran", "cpgplot"/' setup.py
sed -i '/^include_dirs =/ainclude_dirs.append(os.environ\["FFTW_LIB"\])' setup.py
sed -i '/^presto_library_dirs =/apresto_library_dirs.append(os.environ\["FFTW_LIB"\])' setup.py
# python2 setup.py config --compiler=intelem --fcompiler=intelem build_clib --compiler=intelem build_ext --inplace --fcompiler=intelem --compiler=intelem
pip install .

echo -e "\033[41;36m pip install presto finish. \033[0m"
