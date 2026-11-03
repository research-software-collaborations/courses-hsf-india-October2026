# cf. https://github.com/CHTC/templates-GPUs/tree/master/containers/pixi
ARG CUDA_VERSION="13"
ARG ENVIRONMENT="default"

FROM ghcr.io/prefix-dev/pixi:noble AS build

# Redeclaring ARGS in a stage without a value inherits the global default
ARG CUDA_VERSION
ARG ENVIRONMENT

WORKDIR /app
COPY binder/pixi.toml binder/pixi.lock ./
# Image builds have no GPU, so the __cuda virtual package must be overridden
ENV CONDA_OVERRIDE_CUDA=$CUDA_VERSION
RUN pixi install --locked --environment $ENVIRONMENT

## install opencode
# Run through Pixi as the install script needs curl from the environment
RUN pixi run --locked --environment $ENVIRONMENT bash -c \
    'curl -fsSL https://opencode.ai/v2/install | bash -s -- --no-modify-path'

# Optional: trim unused MKL dispatch libs (~170MB). Only what is left here gets
# copied into the final stage, so this does not need to share a RUN with the install.
# Check CPU with: grep -o 'avx512f\|avx2' /proc/cpuinfo | sort -u | head -1
# Uncomment ONE set:
## AVX2 cluster (older Intel Xeon, many AMD EPYC):
#RUN cd /app/.pixi/envs/$ENVIRONMENT/lib && rm -f libmkl_def.so.3 libmkl_avx512.so.3 libmkl_avx10.so.3
## AVX-512 cluster (Intel Xeon Scalable Gold/Platinum 2017+):
#RUN cd /app/.pixi/envs/$ENVIRONMENT/lib && rm -f libmkl_def.so.3 libmkl_avx2.so.3 libmkl_avx10.so.3

# Activate ENVIRONMENT at container runtime by using the Pixi environment
# activation script as the container ENTRYPOINT.
# Set fallback environmental variables to guard against batch system defaults.
# The shell hook sets PATH to its value at build time, so add the runtime user's
# 'pixi global' bin directory after it. It goes last so that the course environment
# takes precedence over globally installed tools.
# setup-work-dir.sh runs after activation as it needs gitpuller from the environment.
RUN echo "#!/usr/bin/env bash" > /app/entrypoint.sh && \
    echo 'export USER="${USER:-$(id -u)}"' >> /app/entrypoint.sh && \
    echo 'export LOGNAME="${LOGNAME:-$USER}"' >> /app/entrypoint.sh && \
    echo '[ -w "${HOME:-/}" ] || export HOME="$(mktemp -d)"' >> /app/entrypoint.sh && \
    pixi shell-hook --environment $ENVIRONMENT --shell bash >> /app/entrypoint.sh && \
    echo 'export PATH="${PATH}:${PIXI_HOME:-$HOME/.pixi}/bin"' >> /app/entrypoint.sh && \
    echo '/usr/local/bin/setup-work-dir.sh' >> /app/entrypoint.sh && \
    echo 'exec "$@"' >> /app/entrypoint.sh && \
    chmod 0755 /app/entrypoint.sh

FROM ghcr.io/prefix-dev/pixi:noble AS final

ARG ENVIRONMENT
ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=57440
ARG WORKSHOP_NAME=mandi26
ARG COURSE_REPO=https://github.com/research-software-collaborations/courses-hsf-india-October2026
ARG COURSE_BRANCH=mandi

ENV SHELL=/bin/bash
ENV WORKSHOP_NAME=$WORKSHOP_NAME
ENV COURSE_REPO=$COURSE_REPO
ENV COURSE_BRANCH=$COURSE_BRANCH

# The base image's unused ubuntu user holds UID 1000, which NB_UID needs
RUN userdel --remove ubuntu && \
    groupadd --gid "${NB_GID}" "${NB_USER}" && \
    useradd --create-home --shell /bin/bash --uid "${NB_UID}" --gid "${NB_GID}" "${NB_USER}"

# Ubuntu's /etc/bash.bashrc has a "sudo hint" block that runs 'groups' in every
# interactive shell. When JupyterHub gives the pod a supplementary group that has no
# name in /etc/group (e.g. GID 109), every terminal then prints
# "groups: cannot find name for group ID 109". sudo is not installed in the image, so
# the block can never print its hint, and removing it only removes that message.
# The grep fails the build if the block changes such that a 'groups' call remains.
RUN sed -i '/^# sudo hint$/,/^fi$/d' /etc/bash.bashrc && \
    ! grep -q 'groups' /etc/bash.bashrc

# Enable Git tab completions in interactive shells, so that users do not have to
# source the completion script themselves.
# The base image has no bash-completion, but git from the Pixi environment ships its
# completion script. /etc/bash.bashrc is read by interactive shells, and Ubuntu's
# /etc/profile also sources it for the login shells that JupyterLab terminals start.
# Unlike ~/.bashrc, it is not hidden if the hub mounts a home directory volume.
RUN printf '\n# Enable Git tab completions\nif [ -f %s ]; then\n    . %s\nfi\n' \
        "/app/.pixi/envs/${ENVIRONMENT}/share/bash-completion/completions/git" \
        "/app/.pixi/envs/${ENVIRONMENT}/share/bash-completion/completions/git" \
        >> /etc/bash.bashrc

WORKDIR /app
# Owned by the notebook user so that the environment and .pixi stay writable at runtime
COPY --from=build --chown=${NB_UID}:${NB_GID} /app/.pixi/envs/$ENVIRONMENT /app/.pixi/envs/$ENVIRONMENT
COPY --from=build --chown=${NB_UID}:${NB_GID} /app/pixi.toml /app/pixi.toml
COPY --from=build --chown=${NB_UID}:${NB_GID} /app/pixi.lock /app/pixi.lock
# The ignore files are needed for 'pixi run' to work in the container
COPY --from=build --chown=${NB_UID}:${NB_GID} /app/.pixi/.gitignore /app/.pixi/.gitignore
COPY --from=build --chown=${NB_UID}:${NB_GID} /app/.pixi/.condapackageignore /app/.pixi/.condapackageignore
COPY --from=build /app/entrypoint.sh /app/entrypoint.sh

COPY --chmod=0755 binder/setup-work-dir.sh /usr/local/bin/setup-work-dir.sh

COPY --from=build /root/.opencode/bin/opencode /usr/local/bin/opencode
## pre-configure opencode with NRP provider (reads the API key from ~/.nrp-llm-token)
COPY --chown=${NB_UID}:${NB_GID} binder/opencode.jsonc /home/${NB_USER}/.config/opencode/opencode.jsonc

## remove the news
COPY --chown=${NB_UID}:${NB_GID} binder/overrides.json /app/.pixi/envs/$ENVIRONMENT/share/jupyter/lab/settings/overrides.json

## serve files through the ~/work symlink to /data that setup-work-dir.sh creates
# Sets the Jupyter root directory to / and opens JupyterLab in the home directory.
# See the comments in binder/jupyter_server_config.py for why.
COPY --chown=${NB_UID}:${NB_GID} binder/jupyter_server_config.py /app/.pixi/envs/$ENVIRONMENT/etc/jupyter/jupyter_server_config.py

USER $NB_USER
# Otherwise the entrypoint falls back to the numeric UID, which setup-work-dir.sh
# would use as the work directory name when JUPYTERHUB_USER is not set
ENV USER=$NB_USER
WORKDIR /home/$NB_USER
RUN echo "export PS1='\[\e[0;32m\]\w\$\[\e[0m\] '" >> .bashrc

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD [ "/bin/bash" ]
