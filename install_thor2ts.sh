#!/bin/bash
set -euo pipefail

RED="\e[31m"
GREEN="\e[32m"
NC="\e[0m"

error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
    exit 1
}

info() {
    echo -e "${GREEN}$1${NC}"
}

info "Checking prerequisites..."
command -v python3 &>/dev/null || error "python3 is not installed. Please install it before continuing."
python3 -c "import venv" &>/dev/null || error "The Python venv module is not available. Please install it (e.g., on Debian/Ubuntu: sudo apt install python3-venv)."

VENV_NAME="venv-thor2ts"

if [ ! -d "$VENV_NAME" ]; then
    info "Creating virtual environment..."
    python3 -m venv "$VENV_NAME" || error "Failed to create virtual environment"
fi

info "Activating virtual environment..."
source "$VENV_NAME/bin/activate" || error "Failed to activate virtual environment"

info "Installing thor_ts_mapper..."
pip install . || error "Failed to install thor_ts_mapper"

command -v thor2ts &>/dev/null || error "Installation failed: thor2ts command not found"
info "Installation complete!"

echo "Usage:"
echo "  thor2ts --help       # Display help information"
echo ""
echo "To use thor2ts in the future, activate the virtual environment by running:"
echo "  source $VENV_NAME/bin/activate"