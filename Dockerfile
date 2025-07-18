FROM archlinux:base-devel

RUN pacman -Syu --noconfirm && \
	pacman -S --noconfirm git sudo base-devel gunicorn python python-pip

# Create a non-root builder user
RUN useradd -m builder && \
    echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder


USER builder
WORKDIR /home/builder
RUN git clone https://aur.archlinux.org/yay-bin.git && \
	cd yay-bin && \
	makepkg -si --noconfirm && \
	rm -rf /home/builder/yay-bin

RUN yay -S --noconfirm \
	siril-git

USER root

RUN pacman -S --noconfirm --needed python-setuptools

# Install pysiril from source
RUN git clone https://gitlab.com/free-astro/pysiril.git /tmp/pysiril && \
    cd /tmp/pysiril && \
    python setup.py bdist_wheel && \
    pip install dist/pysiril-*.whl --break-system-packages && \
    rm -rf /tmp/pysiril

# Create application user
RUN useradd -m appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

USER appuser
WORKDIR /app

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]