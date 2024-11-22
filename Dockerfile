# Utiliser l'image officielle de Python 3.11 basée sur CUDA 12.1.0 et Ubuntu 22.04
FROM python:3.11

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de votre application dans le conteneur
COPY ./app /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Donner la permission d'exécution aux scripts
RUN chmod +x /app/install.sh /app/start.sh

# Exposer les ports si votre application écoute sur des ports spécifiques
EXPOSE 5000
EXPOSE 5443

# Installer les dépendances Python spécifiées dans install.sh
RUN /app/install.sh

# Définir le répertoire HOME (optionnel si nécessaire)
ENV HOME=/app

# Définir la commande par défaut pour exécuter l'application
CMD ["/app/start.sh"]
