# Étape 1 : Utilisez une image officielle de Node.js
FROM node:18-alpine

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier les fichiers de package et installer les dépendances
COPY package*.json ./
RUN npm install

# Étape 4 : Copier le reste du projet
COPY . .

# Étape 5 : Compiler le TypeScript
RUN npm run build

# Étape 6 : Renommer index.js en index.mjs
RUN mv dist/index.js dist/index.mjs

# Étape 7 : Exposer le port (si l'application utilise un serveur)
EXPOSE 3000

# Étape 8 : Définir la commande par défaut pour démarrer l'application
CMD ["node", "--experimental-specifier-resolution=node", "dist/index.mjs"]
