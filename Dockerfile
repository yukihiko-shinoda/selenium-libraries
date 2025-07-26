FROM node:24.4.1-bookworm-slim
RUN npm install -g @anthropic-ai/claude-code
RUN apt-get update && apt-get install -y --no-install-recommends \
    # To set up the PPA
    wget/stable \
    # To add apt-key to set up the PPA
    gnupg/stable \
    # To install the Chromedriver
    unzip/stable \
    # To run as the user: selenium
    sudo/stable \
    # To have a virtual screen to run selenium as headless
    # - Answer: selenium - What is difference between Xvfb and Chromedriver and when to use them - Stack Overflow
    #   https://stackoverflow.com/a/41460456/12721873
    xvfb/stable \
    # - pythonでseleniumを使ってスクリーンショットを撮ると、日本語が文字化けしてしまう | プログラミング学習サイト【侍テラコヤ】
    #   https://terakoya.sejuku.net/question/detail/33885)
    fonts-ipafont-gothic/stable \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
# See:
# - Dockerfile with chromedriver
#   https://gist.github.com/varyonic/dea40abcf3dd891d204ef235c6e8dd79
# - Linux Software Repositories – Google
#   https://www.google.com/linuxrepositories/
# Set up the Chrome PPA
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# --no-check-certificate: 
# - Answer: ubuntu - gpg: no valid OpenPGP data found - Stack Overflow
#   https://stackoverflow.com/a/38039880/12721873
RUN wget --no-check-certificate -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
# Update the package list and install chrome
RUN apt-get update && apt-get install -y --no-install-recommends google-chrome-stable/stable \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_VERSION=138.0.7204.157
ENV CHROMEDRIVER_DIR=/chromedriver
RUN mkdir $CHROMEDRIVER_DIR \
# - Chrome for Testing availability
#   https://googlechromelabs.github.io/chrome-for-testing/
 && wget -q --continue -P $CHROMEDRIVER_DIR https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip \
 && unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR
# Put Chromedriver into the PATH
ENV PATH=$CHROMEDRIVER_DIR:$PATH
WORKDIR /workspace
RUN groupadd -g 1001 selenium \
 && useradd -m -s /bin/bash -u 1001 -g 1001 selenium \
 && install -d -o selenium -g root /workspace/.selenium-cache \
 && chown -R selenium:selenium /workspace
COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /uvx /bin/
# The uv command also errors out when installing semgrep:
# - Getting semgrep-core in pipenv · Issue #2929 · semgrep/semgrep
#   https://github.com/semgrep/semgrep/issues/2929#issuecomment-818994969
ENV SEMGREP_SKIP_BIN=true
USER selenium
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
ENTRYPOINT [ "uv", "run" ]
CMD ["pytest"]
