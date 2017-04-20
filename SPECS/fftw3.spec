# Antia Lamas-Linares
# 2017-01-30
# Modified for KNL deployment and avx512
#
# Important Build-Time Environment Variables (see name-defines.inc)
# NO_PACKAGE=1    -> Do Not Build/Rebuild Package RPM
# NO_MODULEFILE=1 -> Do Not Build/Rebuild Modulefile RPM
#
# Important Install-Time Environment Variables (see post-defines.inc)
# VERBOSE=1       -> Print detailed information at install time
# RPM_DBPATH      -> Path To Non-Standard RPM Database Location
#
# Typical Command-Line Example:
# ./build_rpm.sh Bar.spec
# cd ../RPMS/x86_64
# rpm -i --relocate /tmprpm=/opt/apps Bar-package-1.1-1.x86_64.rpm
# rpm -i --relocate /tmpmod=/opt/apps Bar-modulefile-1.1-1.x86_64.rpm
# rpm -e Bar-package-1.1-1.x86_64 Bar-modulefile-1.1-1.x86_64

Summary: A Nice little relocatable skeleton spec file example.

# Give the package a base name
%define pkg_base_name fftw3
%define MODULE_VAR    FFTW3

# Create some macros (spec file variables)
%define major_version 3
%define minor_version 3
%define micro_version 6

%define pkg_version %{major_version}.%{minor_version}.%{micro_version}

### Toggle On/Off ###
%include rpm-dir.inc                  
%include compiler-defines.inc
%include mpi-defines.inc
########################################
### Construct name based on includes ###
########################################
#%include name-defines.inc
%include name-defines-noreloc.inc
#%include name-defines-hidden.inc
#%include name-defines-hidden-noreloc.inc
########################################
############ Do Not Remove #############
########################################

############ Do Not Change #############
Name:      %{pkg_name}
Version:   %{pkg_version}
BuildRoot: /var/tmp/%{pkg_name}-%{pkg_version}-buildroot
########################################

Release:   1%{?dist}
License:   GPL
Group:     System Environment/Base
URL:       http://www.fftw.org
Packager:  TACC - alamas@tacc.utexas.edu
Source:    fftw-%{pkg_version}-pl2.tar.gz

# Turn off debug package mode
%define debug_package %{nil}
%define dbg           %{nil}


%package %{PACKAGE}
Summary: The package RPM
Group: Development/Tools
%description package
This is the long description for the package RPM...
FFTW is a C subroutine library for computing the discrete Fourier transform
(DFT) in one or more dimensions, of arbitrary input size, and of both real and
complex data (as well as of even/odd data, i.e. the discrete cosine/sine
transforms or DCT/DST). 

%package %{MODULEFILE}
Summary: The modulefile RPM
Group: Lmod/Modulefiles
%description modulefile
This is the long description for the modulefile RPM...
FFTW is a C subroutine library for computing the discrete Fourier transform
(DFT) in one or more dimensions, of arbitrary input size, and of both real and
complex data (as well as of even/odd data, i.e. the discrete cosine/sine
transforms or DCT/DST). 

%description
FFTW is a C subroutine library for computing the discrete Fourier transform
(DFT) in one or more dimensions, of arbitrary input size, and of both real and
complex data (as well as of even/odd data, i.e. the discrete cosine/sine
transforms or DCT/DST). 

#---------------------------------------
%prep
#---------------------------------------

#------------------------
%if %{?BUILD_PACKAGE}
#------------------------
  # Delete the package installation directory.
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}

%setup -n fftw-%{pkg_version}-pl2

#-----------------------
%endif # BUILD_PACKAGE |
#-----------------------

#---------------------------
%if %{?BUILD_MODULEFILE}
#---------------------------
  #Delete the module installation directory.
  rm -rf $RPM_BUILD_ROOT/%{MODULE_DIR}
#--------------------------
%endif # BUILD_MODULEFILE |
#--------------------------



#---------------------------------------
%build
#---------------------------------------


#---------------------------------------
%install
#---------------------------------------

# Setup modules
%include system-load.inc
module purge
# Load Compiler
%include compiler-load.inc
# Load MPI Library
%include mpi-load.inc

# Insert further module commands

echo "Building the package?:    %{BUILD_PACKAGE}"
echo "Building the modulefile?: %{BUILD_MODULEFILE}"

#------------------------
%if %{?BUILD_PACKAGE}
#------------------------

  mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}
  
  #######################################
  ##### Create TACC Canary Files ########
  #######################################
  touch $RPM_BUILD_ROOT/%{INSTALL_DIR}/.tacc_install_canary
  #######################################
  ########### Do Not Remove #############
  #######################################

  #========================================
  # Insert Build/Install Instructions Here
  #========================================


#
# Insert vectorization and optimization flags
# for gcc-specific builds
#

export ncores=12

##
## Configure and make double-precision version w/ mpi support
##
./configure                   \
--with-pic                    \
--enable-shared               \
--enable-openmp               \
--enable-threads              \
--disable-dependency-tracking \
--enable-mpi                  \
--enable-sse2                 \
--prefix=%{INSTALL_DIR}

make -j ${ncores}
make DESTDIR=$RPM_BUILD_ROOT install

make clean
##
## Configure and make single-precision version /w mpi support
##

#
# Insert configure for single-precision version
#

make -j ${ncores}
make DESTDIR=$RPM_BUILD_ROOT install

  
#-----------------------  
%endif # BUILD_PACKAGE |
#-----------------------


#---------------------------
%if %{?BUILD_MODULEFILE}
#---------------------------

  mkdir -p $RPM_BUILD_ROOT/%{MODULE_DIR}
  
  #######################################
  ##### Create TACC Canary Files ########
  #######################################
  touch $RPM_BUILD_ROOT/%{MODULE_DIR}/.tacc_module_canary
  #######################################
  ########### Do Not Remove #############
  #######################################
  
# Write out the modulefile associated with the application
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/%{MODULE_FILENAME} << 'EOF'
local help_message=[[
FFTW is a C subroutine library for computing the discrete Fourier transform
(DFT) in one or more dimensions, of arbitrary input size, and of both real and
complex data (as well as of even/odd data, i.e. the discrete cosine/sine
transforms or DCT/DST). 

The FFTW %{version} modulefile defines the following environment variables:
TACC_%{MODULE_VAR}_DIR, TACC_%{MODULE_VAR}_LIB, and TACC_%{MODULE_VAR}_INC
for the location of the FFTW %{version} distribution,
libraries, and include files, respectively.

To use the %{MODULE_VAR} library, compile your source code with:

	-I$TACC_%{MODULE_VAR}_INC

and add the following options to the link step for serial codes:

	-Wl,-rpath,$TACC_%{MODULE_VAR}_LIB  -L$TACC_%{MODULE_VAR}_LIB -lfftw3

for MPI codes:

	-Wl,-rpath,$TACC_%{MODULE_VAR}_LIB -L$TACC_%{MODULE_VAR}_LIB -lfftw3_mpi -lfftw3

In addition, a single-precision fftw library is also available
by adding an 'f' suffix to the library names above:

(serial):	-L$TACC_%{MODULE_VAR}_LIB -lfftw3f
(mpi): 		-L$TACC_%{MODULE_VAR}_LIB -lfftw3f_mpi -lfftw3f


Version %{version}
]]

help(help_message,"\n")

-- Fill out the whatis section; use previous wokr


local fftw_dir="%{INSTALL_DIR}"

-- Set up DIR, LIB, and INC TACC variables


--
-- Append to LD_LIBRARY_PATH, PATH, MANPATH, and PKG_CONFIG_PATH
--

EOF

cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module3.1.1#################################################
##
## version file for %{pkg_base_name}/%{version}
##

set     ModulesVersion      "%{version}"
EOF
  
  # Check the syntax of the generated lua modulefile only if a visible module
  %if %{?VISIBLE}
    %{SPEC_DIR}/checkModuleSyntax $RPM_BUILD_ROOT/%{MODULE_DIR}/%{MODULE_FILENAME}
  %endif
#--------------------------
%endif # BUILD_MODULEFILE |
#--------------------------


#------------------------
%if %{?BUILD_PACKAGE}
%files package
#------------------------

  %defattr(-,root,install,)
  # RPM package contains files within these directories
  %{INSTALL_DIR}

#-----------------------
%endif # BUILD_PACKAGE |
#-----------------------
#---------------------------
%if %{?BUILD_MODULEFILE}
%files modulefile 
#---------------------------

  %defattr(-,root,install,)
  # RPM modulefile contains files within these directories
  %{MODULE_DIR}

#--------------------------
%endif # BUILD_MODULEFILE |
#--------------------------

########################################
## Fix Modulefile During Post Install ##
########################################
%post %{PACKAGE}
export PACKAGE_POST=1
%include post-defines.inc
%post %{MODULEFILE}
export MODULEFILE_POST=1
%include post-defines.inc
%preun %{PACKAGE}
export PACKAGE_PREUN=1
%include post-defines.inc
########################################
############ Do Not Remove #############
########################################

#---------------------------------------
%clean
#---------------------------------------
rm -rf $RPM_BUILD_ROOT
