#
# W. Cyrus Proctor
# 2015-11-20 Need to investigate relocation -- use /opt/apps for now
# 2015-11-20
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
%define pkg_base_name openmpi
%define MODULE_VAR    OPENMPI

# Create some macros (spec file variables)
%define major_version 2
%define minor_version 1
%define micro_version 0

%define pkg_version %{major_version}.%{minor_version}.%{micro_version}
%define pkg_version_dash %{major_version}_%{minor_version}

### Toggle On/Off ###
%include rpm-dir.inc                  
%include compiler-defines.inc
###%include mpi-defines.inc
########################################
### Construct name based on includes ###
########################################
%include name-defines-noreloc.inc
########################################
############ Do Not Remove #############
########################################
%define mpi_fam_ver   %{pkg_base_name}_%{pkg_version_dash}

############ Do Not Change #############
Name:      %{pkg_name}
Version:   %{pkg_version}
BuildRoot: /var/tmp/%{pkg_name}-%{pkg_version}-buildroot
########################################

Release:   1
License:   BSD
Group:     MPI
URL:       https://www.open-mpi.org
Packager:  TACC - cproctor@tacc.utexas.edu
Source:    openmpi-%{pkg_version}.tar.gz

# Turn off debug package mode
%define debug_package %{nil}
%define dbg           %{nil}


%package %{PACKAGE}
Summary: The package RPM
Group: Development/Tools
%description package
This is the long description for the package RPM...
The Open MPI Project is an open source Message Passing Interface implementation
that is developed and maintained by a consortium of academic, research, and
industry partners. Open MPI is therefore able to combine the expertise,
technologies, and resources from all across the High Performance Computing
community in order to build the best MPI library available. Open MPI offers
advantages for system and software vendors, application developers and computer
science researchers.

%package %{MODULEFILE}
Summary: The modulefile RPM
Group: Lmod/Modulefiles
%description modulefile
This is the long description for the modulefile RPM...
The Open MPI Project is an open source Message Passing Interface implementation
that is developed and maintained by a consortium of academic, research, and
industry partners. Open MPI is therefore able to combine the expertise,
technologies, and resources from all across the High Performance Computing
community in order to build the best MPI library available. Open MPI offers
advantages for system and software vendors, application developers and computer
science researchers.

%description
The Open MPI Project is an open source Message Passing Interface implementation
that is developed and maintained by a consortium of academic, research, and
industry partners. Open MPI is therefore able to combine the expertise,
technologies, and resources from all across the High Performance Computing
community in order to build the best MPI library available. Open MPI offers
advantages for system and software vendors, application developers and computer
science researchers.

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

# Insert necessary module commands
ml purge
# Load Compiler
%include compiler-load.inc
# Load MPI Library
#%include mpi-load.inc

# Insert further module commands
ml

echo "Building the package?:    %{BUILD_PACKAGE}"
echo "Building the modulefile?: %{BUILD_MODULEFILE}"

#------------------------
%if %{?BUILD_PACKAGE}
#------------------------

  mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}
  mkdir -p %{INSTALL_DIR}
  mount -t tmpfs tmpfs %{INSTALL_DIR}
    
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
 
 

if [ "%{comp_fam}" == "gcc" ]; then
  export CFLAGS="-march=westmere -mtune=westmere"
  export CXXFLAGS="-march=westmere -mtune=westmere"
  export FCFLAGS="-march=westmere -mtune=westmere"
  export LDFLAGS="-march=westmere -mtune=westmere"
elif [ "%{comp_fam}" == "intel" ]; then
  export CFLAGS="-xSSE4.2"
  export CXXFLAGS="-xSSE4.2"
  export FCFLAGS="-xSSE4.2"
  export LDFLAGS="-xSSE4.2"
else
  echo "Unrecognized compiler! Exiting!"
  exit -1
fi

export ncores=12

./configure                                      \
--prefix=%{INSTALL_DIR}                          \
--enable-orterun-prefix-by-default               \
--with-verbs                                     \
--disable-dlopen                                 \
--disable-oshmem                                 \
--with-slurm                                     \
--with-pmi-libdir=/usr/lib64                     \
--enable-static                                  \
--disable-shared

make -j ${ncores}
make -j ${ncores} install


if [ ! -d $RPM_BUILD_ROOT/%{INSTALL_DIR} ]; then
  mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}
fi

cp -r %{INSTALL_DIR}/ $RPM_BUILD_ROOT/%{INSTALL_DIR}/..
umount %{INSTALL_DIR}/
  



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
The Open MPI Project is an open source Message Passing Interface implementation
that is developed and maintained by a consortium of academic, research, and
industry partners. Open MPI is therefore able to combine the expertise,
technologies, and resources from all across the High Performance Computing
community in order to build the best MPI library available. Open MPI offers
advantages for system and software vendors, application developers and computer
science researchers.

This module loads the openmpi environment built with
Intel compilers. By loading this module, the following commands
will be automatically available for compiling MPI applications:
mpif77       (F77 source)
mpif90       (F90 source)
mpicc        (C   source)
mpiCC/mpicxx (C++ source)

The %{MODULE_VAR} module also defines the following environment variables:
TACC_%{MODULE_VAR}_DIR, TACC_%{MODULE_VAR}_LIB, TACC_%{MODULE_VAR}_INC and
TACC_%{MODULE_VAR}_BIN for the location of the %{MODULE_VAR} distribution, libraries,
include files, and tools respectively.

Version %{version}
]]

--help(help_msg)
help(help_msg)


whatis("Name: %{pkg_base_name}"                                              )
whatis("Version: %{version}"                                                 )
whatis("Category: MPI library, Runtime Support"                              )
whatis("Description: OpenMPI Library (C/C++/Fortran for x86_64)"             )
whatis("URL: https://www.open-mpi.org"                                       )


-- Create environment variables
local base = "%{INSTALL_DIR}"

setenv( "MPICH_HOME"                  ,           base                       )
setenv( "TACC_MPI_GETMODE"            ,           "openmpi_ssh"              )

prepend_path( "PATH"                  , pathJoin( base, "bin"                ))
prepend_path( "LD_LIBRARY_PATH"       , pathJoin( base, "lib"                ))
prepend_path( "MANPATH"               , pathJoin( base, "share/man"          ))
prepend_path( "MODULEPATH"            , "%{MODULE_PREFIX}/%{comp_fam_ver}/%{mpi_fam_ver}/modulefiles")

setenv("TACC_%{MODULE_VAR}_DIR"       ,           base                       )
setenv("TACC_%{MODULE_VAR}_BIN"       , pathJoin( base, "bin"                ))
setenv("TACC_%{MODULE_VAR}_LIB"       , pathJoin( base, "lib"                ))
setenv("TACC_%{MODULE_VAR}_INC"       , pathJoin( base, "include"            ))

family("MPI")

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

