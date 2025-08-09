FROM archlinux:latest

RUN pacman -Syu --noconfirm \
    && pacman -S --noconfirm curl rust ffmpeg python-pip python-virtualenv ca-certificates poppler pandoc \
    && pacman -Scc --noconfirm

# Create config directory and files for noted.md
RUN mkdir -p /root/.config/notedmd
RUN cat <<EOF > /root/.config/notedmd/config.toml
active_provider = "gemini"

[gemini]
api_key = "ai"
EOF

RUN cat <<EOF > /root/.config/notedmd/progress.json
{
  "files": {}
}
EOF


# Install uv
RUN curl -fsSL https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app
COPY . .

# Install Python 3.10 with uv
RUN uv python install 3.10

# (Optional) Pin project Python version
RUN uv python pin 3.10

# Create virtual environment specifying Python version correctly
RUN uv venv /opt/venv --python=3.10

ENV PATH="/opt/venv/bin:$PATH"

RUN python -m ensurepip --upgrade
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot/main.py"]