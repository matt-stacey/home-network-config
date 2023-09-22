oldwd=`pwd`

# Parse arguments
overwrite_venv=
while (( $# )); do
    case $1 in
        --overwrite-venv)
            overwrite_venv=1
            ;;
        --*)
            echo 'bad option: '$1
            ;;
        *)
            echo $1' not parsed'
            ;;
    esac
    shift
done

# Set up environment variables
export PROJECT_ROOT=`git rev-parse --show-toplevel`

# Set up script variables
proj_name=salt
venv_path=${PROJECT_ROOT}/${proj_name}_python3

# Create virtual environment
if [ $overwrite_venv ]; then
    deactivate
    rm -rf $venv_path
fi

if [ ! -d ${venv_path} ]; then
    python3 -m venv ${venv_path}  # python3 not standard
    source ${PROJECT_ROOT}/${proj_name}_python3/bin/activate
    python -m pip install -r ${PROJECT_ROOT}/python_requirements.txt
else
    source ${PROJECT_ROOT}/${proj_name}_python3/bin/activate
fi

# Return command line to proper location
cd $oldwd
