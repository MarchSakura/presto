#!/usr/bin/bash

echo -e "\033[41;36m Deployment beginning... \033[0m"

export BUILD_PATH=$PWD
FCC=gfortran
F77=gfortran
CC=gcc

echo -e "\033[41;37m Making src and lib dictionary beginning... \033[0m"

mkdir $BUILD_PATH/src
mkdir $BUILD_PATH/lib

echo -e "\033[42;37m Making src and lib dictionary finish. \033[0m"

# install fftw
echo -e "\033[41;37m install fftw beginning... \033[0m"

tar -xzvf $BUILD_PATH/download/fftw-3.3.9.tar.gz -C $BUILD_PATH/src
mkdir $BUILD_PATH/lib/fftw-3.3.9
export FFTW_INSTALL=$BUILD_PATH/src/fftw-3.3.9
# pure version fftw
mkdir $BUILD_PATH/lib/fftw-3.3.9/gcc-pure
export FFTW=$BUILD_PATH/lib/fftw-3.3.9/gcc-pure
cd $FFTW_INSTALL
./configure --enable-single --enable-shared --prefix=$FFTW
make -j all
make install
cd $BUILD_PATH

# # high intrinsic + threads + openmp  version fftw
# mkdir $BUILD_PATH/lib/fftw-3.3.9/gcc-avx-threads
# export FFTW=$BUILD_PATH/lib/fftw-3.3.9/gcc-avx-threads
# cd $FFTW_INSTALL
# ./configure --enable-single --enable-shared --enable-sse --enable-sse2 --enable-avx --enable-avx2 --enable-avx512 --enable-avx-128-fma --enable-threads --enable-openmp --prefix=$FFTW
# make -j all
# make install
# cd $BUILD_PATH

# module load intel/2020
# FCC=ifort
# F77=ifort
# CC=icc

# pure version fftw
# mkdir $BUILD_PATH/lib/fftw-3.3.9/icc-pure
# export FFTW=$BUILD_PATH/lib/fftw-3.3.9/icc-pure
# cd $FFTW_INSTALL
# ./configure --enable-single --enable-shared --prefix=$FFTW CC=icc F77=ifort
# make -j all
# make install
# cd $BUILD_PATH

# # high intrinsic + threads + openmp  version fftw
# mkdir $BUILD_PATH/lib/fftw-3.3.9/icc-avx-threads
# export FFTW=$BUILD_PATH/lib/fftw-3.3.9/icc-avx-threads
# cd $FFTW_INSTALL
# ./configure --enable-single --enable-shared --enable-sse --enable-sse2 --enable-avx --enable-avx2 --enable-avx512 --enable-threads --enable-openmp --prefix=$FFTW CC=icc F77=ifort
# make -j all
# make install
# cd $BUILD_PATH

echo -e "\033[42;37m install fftw end. \033[0m"

# install pgplot

echo -e "\033[41;37m install pgplot beginning... \033[0m"

tar -xzvf $BUILD_PATH/download/pgplot5.2.tar.gz -C $BUILD_PATH/src/
mkdir $BUILD_PATH/lib/pgplot
export PGPLOT=$BUILD_PATH/lib/pgplot
cd $PGPLOT
cp $BUILD_PATH/src/pgplot/drivers.list .  
sed -i '\%XWDRIV%s/^! //' drivers.list
sed -i '\%PSDRIV%s/^! //' drivers.list
$BUILD_PATH/src/pgplot/makemake $BUILD_PATH/src/pgplot linux g77_gcc
make CCOMPL=$CC FCOMPL=$FCC
make cpg CCOMPL=$CC FCOMPL=$FCC
cd $BUILD_PATH


echo -e "\033[42;37m install pgplot end. \033[0m"

# # install TEMPO
echo -e "\033[41;37m install TEMPO beginning... \033[0m"

cp -rf $BUILD_PATH/download/tempo/ $BUILD_PATH/lib
export TEMPO=$BUILD_PATH/lib/tempo
cd $TEMPO
./prepare
./configure --prefix=$TEMPO
make
make install
cd $BUILD_PATH

echo -e "\033[42;37m install TEMPO end. \033[0m"

# # install cfitsio
echo -e "\033[41;37m install cfitsio beginning... \033[0m"

tar -xzvf $BUILD_PATH/download/cfitsio-3.49.tar.gz -C $BUILD_PATH/src
export CFITSIO_INSTALL=$BUILD_PATH/src/cfitsio-3.49
mkdir $BUILD_PATH/lib/cfitsio
export CFITSIO=$BUILD_PATH/lib/cfitsio
cd $CFITSIO_INSTALL
./configure --prefix=$CFITSIO
make
make install
cd $BUILD_PATH

echo -e "\033[42;37m install cfitsio end. \033[0m"

# extract presto-3
echo -e "\033[41;37m extract presto-3 beginning... \033[0m"

#tar xzvf $BUILD_PATH/download/v3.0.1.tar.gz -C .
export PRESTO=$BUILD_PATH/presto-3.0.1
# export C_INCLUDE_PATH=$PRESTO/include:$FFTW/include:$CFITSIO/include:$C_INCLUDE_PATH
# export LD_LIBRARY_PATH=$FFTW/lib:$CFITSIO/lib:$PRESTO/lib:$LD_LIBRARY_PATH
# export PKG_CONFIG_PATH=$CFITSIO/lib/pkgconfig:$FFTW/lib/pkgconfig:$PKG_CONFIG_PATH
# export PGPLOT_DIR=$PGPLOT
# export FFTW_LIB=$FFTW/lib

# cd $PRESTO/src
# sed -i '\%pkg-config --cflags%s/pkg-config/PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 pkg-config/' Makefile
# sed -i '\%pkg-config --libs%s/pkg-config/PKG_CONFIG_ALLOW_SYSTEM_LIBS=1 pkg-config/' Makefile
# make makewisdom
# make
# cd $PRESTO/python/presto
# sed -i '\%from presto%s/from presto //' filterbank.py
# sed -i '\%from presto%s/from presto\./from /' sigproc.py
# sed -i '\%from presto%s/from presto //' psrfits.py

# cd $PRESTO
# sed -i '\%\["cpgplot"%s/\["cpgplot"/\["gfortran", "cpgplot"/' setup.py
# sed -i '/^include_dirs =/ainclude_dirs.append(os.environ\["FFTW_LIB"\])' setup.py
# sed -i '/^presto_library_dirs =/apresto_library_dirs.append(os.environ\["FFTW_LIB"\])' setup.py
# pip install .

echo -e "\033[42;37m extract presto-3 end. \033[0m"

# extract test data
tar xvf $BUILD_PATH/download/PRESTO_Data.tar.gz -C $PRESTO
cd $PRESTO/TestData1
sed -i '\%^import sifting%s/import sifting/from presto import sifting/' pipeline.py
sed -i '\%cands\.sort%s/sifting\.cmp_sigma/key=attrgetter("sigma"), reverse=True/' pipeline.py
sed -i 'N;12ifrom operator import itemgetter, attrgetter' pipeline.py
cd $PRESTO/TestData2
sed -i '\%^import sifting%s/import sifting/from presto import sifting/' pipeline.py
sed -i '\%cands\.sort%s/sifting\.cmp_sigma/key=attrgetter("sigma"), reverse=True/' pipeline.py
sed -i 'N;12ifrom operator import itemgetter, attrgetter' pipeline.py
