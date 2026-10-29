#!/bin/bash
# Create per-user work directory on shared volume, symlink ~/work to it,
# and clone/update the course repo inside it via nbgitpuller.
WORKSHOP_NAME="${WORKSHOP_NAME:-workshop}"
RAW_USER="${JUPYTERHUB_USER:-${USER:-jovyan}}"
# Sanitize: replace chars outside [a-zA-Z0-9._-] with underscore
SAFE_USER=$(echo "$RAW_USER" | tr -cs 'a-zA-Z0-9._-' '_')

WORK_DIR="/data/${WORKSHOP_NAME}/${SAFE_USER}"
if mkdir -p "$WORK_DIR" 2>/dev/null; then
    ln -sfn "$WORK_DIR" "/home/jovyan/work"
    if [ -n "${COURSE_REPO:-}" ]; then
        REPO_NAME=$(basename "$COURSE_REPO")
        gitpuller "$COURSE_REPO" "${COURSE_BRANCH:-main}" "$WORK_DIR/$REPO_NAME"
        git -C "$WORK_DIR/$REPO_NAME" submodule update --init 2>/dev/null || true
    fi
fi
