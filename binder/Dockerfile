FROM mambaorg/micromamba:2.9.0

ENV SHELL /bin/bash
ARG NEW_MAMBA_USER=jovyan
ARG NEW_MAMBA_USER_ID=1000
ARG NEW_MAMBA_USER_GID=57440

USER root

RUN if grep -q '^ID=alpine$' /etc/os-release; then \
      # alpine does not have usermod/groupmod
      apk add --no-cache --virtual temp-packages shadow; \
    fi && \
    usermod "--login=${NEW_MAMBA_USER}" "--home=/home/${NEW_MAMBA_USER}" \
        --move-home "-u ${NEW_MAMBA_USER_ID}" "${MAMBA_USER}" && \
    groupmod "--new-name=${NEW_MAMBA_USER}" \
        "-g ${NEW_MAMBA_USER_GID}" "${MAMBA_USER}" && \
    if grep -q '^ID=alpine$' /etc/os-release; then \
      # remove the packages that were only needed for usermod/groupmod
      apk del temp-packages; \
    fi && \
    # Update the expected value of MAMBA_USER for the
    # _entrypoint.sh consistency check.
    echo "${NEW_MAMBA_USER}" > "/etc/arg_mamba_user" && \
    :
ENV MAMBA_USER=$NEW_MAMBA_USER

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git && rm -rf /var/lib/apt/lists/*

USER $MAMBA_USER

COPY binder/environment.yml .

RUN \
    CONDA_OVERRIDE_CUDA="13.2" micromamba env update --name base -f environment.yml && \
    CONDA_OVERRIDE_CUDA="13.2" micromamba install -y  -c conda-forge \
    jupyterlab openssh notebook vim nano emacs curl wget  && \
    micromamba clean --all --yes && \
    rm -rf /opt/conda/pkgs ~/.cache \
    # Optional: trim unused MKL dispatch libs (~170MB). All deletions must be in
    # this same RUN block — a separate RUN layer cannot shrink what was laid down here.
    # Check CPU with: grep -o 'avx512f\|avx2' /proc/cpuinfo | sort -u | head -1
    # Uncomment ONE set:
    ## AVX2 cluster (older Intel Xeon, many AMD EPYC):
    #&& rm -f /opt/conda/lib/libmkl_def.so.3 \
    #         /opt/conda/lib/libmkl_avx512.so.3 \
    #         /opt/conda/lib/libmkl_avx10.so.3 \
    ## AVX-512 cluster (Intel Xeon Scalable Gold/Platinum 2017+):
    #&& rm -f /opt/conda/lib/libmkl_def.so.3 \
    #         /opt/conda/lib/libmkl_avx2.so.3 \
    #         /opt/conda/lib/libmkl_avx10.so.3 \
    && :

RUN micromamba list

USER root

RUN ln=`grep -n "exec " /usr/local/bin/_entrypoint.sh | tail -1 | cut -f1 -d:`; \
    sed -i "${ln}igit clone --recurse-submodules https://github.com/research-software-collaborations/courses-hsf-india-October2026" /usr/local/bin/_entrypoint.sh

## install opencode
RUN curl -fsSL https://opencode.ai/v2/install | bash -s -- --no-modify-path && \
    mv /root/.opencode/bin/opencode /usr/local/bin/opencode
## pre-configure opencode with NRP provider (users set NRP_API_KEY themselves)
COPY binder/opencode.jsonc /tmp/opencode.jsonc
RUN mkdir -p /home/${MAMBA_USER}/.config/opencode && \
    cp /tmp/opencode.jsonc /home/${MAMBA_USER}/.config/opencode/opencode.jsonc && \
    chown -R ${MAMBA_USER}:${MAMBA_USER} /home/${MAMBA_USER}/.config

## remove the news
COPY binder/overrides.json /tmp
RUN mkdir -p /opt/conda/share/jupyter/lab/settings; \
      cp /tmp/overrides.json /opt/conda/share/jupyter/lab/settings

USER $MAMBA_USER
WORKDIR /home/jovyan
RUN echo "export PS1='\[\e[0;32m\]\w\$\[\e[0m\] '" >> .bashrc
