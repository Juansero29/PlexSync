# Étape 1 : Utilisez une image officielle de Node.js
FROM node:18-alpine

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier les fichiers de package et installer les dépendances
COPY package*.json ./
RUN npm install

# Étape 4 : Copier le reste du projet
COPY . .

# Étape 5 : Compiler le TypeScript (optionnel si déjà pré-compilé)
RUN npm run build

# Étape 6 : Exposer le port (si l'application utilise un serveur, par exemple)
EXPOSE 3000

# Étape 7 : Définir la commande par défaut pour démarrer l'application
CMD ["npm", "start"]
