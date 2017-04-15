#
# W. Cyrus Proctor
# 2015-08-25
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
%define pkg_base_name gsl
%define MODULE_VAR    GSL

# Create some macros (spec file variables)
%define major_version 2
%define minor_version 3

%define pkg_version %{major_version}.%{minor_version}

### Toggle On/Off ###
%include rpm-dir.inc                  
%include compiler-defines.inc
#%include mpi-defines.inc
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
Group:     Development/Tools
URL:       http://www.gnu.org/software/gsl
Packager:  TACC - cproctor@tacc.utexas.edu
Source:    %{pkg_base_name}-%{pkg_version}.tar.gz

# Turn off debug package mode
%define debug_package %{nil}
%define dbg           %{nil}


%package %{PACKAGE}
Summary: The package RPM
Group: Development/Tools
%description package
This is the long description for the package RPM...
The GNU Scientific Library (GSL) is a numerical library for C and C++
programmers. It is free software under the GNU General Public License.  The
library provides a wide range of mathematical routines such as random number
generators, special functions and least-squares fitting. There are over 1000
functions in total with an extensive test suite.

%package %{MODULEFILE}
Summary: The modulefile RPM
Group: Lmod/Modulefiles
%description modulefile
This is the long description for the modulefile RPM...
The GNU Scientific Library (GSL) is a numerical library for C and C++
programmers. It is free software under the GNU General Public License.  The
library provides a wide range of mathematical routines such as random number
generators, special functions and least-squares fitting. There are over 1000
functions in total with an extensive test suite.

%description
The GNU Scientific Library (GSL) is a numerical library for C and C++
programmers. It is free software under the GNU General Public License.  The
library provides a wide range of mathematical routines such as random number
generators, special functions and least-squares fitting. There are over 1000
functions in total with an extensive test suite.

#---------------------------------------
%prep
#---------------------------------------

#------------------------
%if %{?BUILD_PACKAGE}
#------------------------
  # Delete the package installation directory.
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}

%setup -n %{pkg_base_name}-%{pkg_version}

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
#%include mpi-load.inc

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
  
 %if "%{is_intel}" == "1" 
  export CFLAGS="-O3 -xSSE4.2"
  export CPPFLAGS="-O3 -xSSE4.2" 
  export LDFLAGS="-O3 -xSSE4.2"
%endif

%if "%{is_gcc}" == "1" 
  export CFLAGS="-O3 -march=westmere -mtune=westmere"
  export CPPFLAGS="-O3 -march=westmere -mtune=westmere"
  export LDFLAGS="-O3 -march=westmere -mtune=westmere"
%endif
 
  export ncores=12 

  ./configure \
  --prefix=%{INSTALL_DIR}

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
local help_msg=[[
The GNU Scientific Library (GSL) is a numerical library for C and C++
programmers. It is free software under the GNU General Public License.  The
library provides a wide range of mathematical routines such as random number
generators, special functions and least-squares fitting. There are over 1000
functions in total with an extensive test suite.

The %{MODULE_VAR} module defines the following environment variables:
TACC_%{MODULE_VAR}_DIR, TACC_%{MODULE_VAR}_LIB, TACC_%{MODULE_VAR}_INC and
TACC_%{MODULE_VAR}_BIN for the location of the %{MODULE_VAR} distribution, libraries,
include files, and tools respectively.

Please compile the source code with the option:

        -I$TACC_%{MODULE_VAR}_INC/gsl -I$TACC_%{MODULE_VAR}_INC  

and add the following to the link step:

        -L$TACC_%{MODULE_VAR}_LIB -lgsl


The %{MODULE_VAR} module prepends to your PATH for access
to %{MODULE_VAR} utilities. It also modifies LD_LIBRARY_PATH.

Version %{version}

]]

--help(help_msg)
help(help_msg)

whatis("Name: %{pkg_base_name}")
whatis("Version: %{pkg_version}")
whatis("Category: library, mathematics")
whatis("Keywords: Library, Mathematics")
whatis("URL: https://www.gnu.org/software/gsl")
whatis("Description: Numerical library for C/C++ programmers")

-- Create environment variables.
local gsl_dir           = "%{INSTALL_DIR}"

prepend_path(    "PATH",                pathJoin(gsl_dir, "bin"))
prepend_path(    "LD_LIBRARY_PATH",     pathJoin(gsl_dir, "lib"))
setenv( "TACC_%{MODULE_VAR}_DIR",                gsl_dir)
setenv( "TACC_%{MODULE_VAR}_INC",       pathJoin(gsl_dir, "include"))
setenv( "TACC_%{MODULE_VAR}_LIB",       pathJoin(gsl_dir, "lib"))
setenv( "TACC_%{MODULE_VAR}_BIN",       pathJoin(gsl_dir, "bin"))

EOF
  
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module3.1.1#################################################
##
## version file for %{BASENAME}%{version}
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

