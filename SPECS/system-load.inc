# Support for the lmod system at TACC
if [ -f "${BASH_ENV}" ]; then
  source ${BASH_ENV}
  module purge
  clearMT
  export MODULEPATH=/opt/apps/modulefiles
  module load TACC
fi
