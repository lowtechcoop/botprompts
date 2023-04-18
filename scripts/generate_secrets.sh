#!/usr/bin/env bash



SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"

GENERAL_ENV="${REPO_DIR}/.env"
BACKEND_ENV_NAME="${REPO_DIR}/secrets/.backend.env"
FRONTEND_ENV_NAME="${REPO_DIR}/secrets/.frontend.env"

DB_DATABASE_NAME="${REPO_DIR}/secrets/db_database.txt"
DB_HOST_NAME="${REPO_DIR}/secrets/db_host.txt"
DB_USERNAME_NAME="${REPO_DIR}/secrets/db_username.txt"
DB_PASSWORD_NAME="${REPO_DIR}/secrets/db_password.txt"
PGADMIN_PASSWORD="${REPO_DIR}/secrets/pgadmin_password.txt"

function checkSecretsFile {
    echo "Checking $1"

    if [[ ! -f "$1" ]]; then
        read -rp "File $1 does not exist, did you want to create it? [y/N]" CONFIRM_CREATE_FILE

        if [[ ${CONFIRM_CREATE_FILE^^} == [yY] ]]; then
            # Check if a ".sample" version exists otherwise just create a blank file
            if [[ -f "${1}.sample" ]]; then
                copy "${1}.sample" "${1}"
            else
                touch "${1}"
            fi
            echo "    File created in ${1}"
        fi

    else
        echo "    File exists, skipping"
    fi
}

echo "Generating secrets in the repository directory: ${REPO_DIR}"
read -rp "Is this the correct directory? [y/N] " CORRECT_DIR_CONFIRM && [[ ${CORRECT_DIR_CONFIRM^^} == [yY] ]] || exit 1

checkSecretsFile "$GENERAL_ENV"
checkSecretsFile "$BACKEND_ENV_NAME"
checkSecretsFile "$FRONTEND_ENV_NAME"
checkSecretsFile "$DB_DATABASE_NAME"
checkSecretsFile "$DB_HOST_NAME"
checkSecretsFile "$DB_USERNAME_NAME"
checkSecretsFile "$DB_PASSWORD_NAME"
checkSecretsFile "$PGADMIN_PASSWORD"

echo "Files created in the right place. Now they need to be updated with credentials"
