# Initialisation Docker

Pour l’étape de déploiement, je vais vous guider pour préparer votre projet avec **Docker** et pour rédiger des instructions claires dans le **README**. Cela rendra votre outil facile à installer, exécuter et partager avec d'autres développeurs.

---

## **1. Utiliser Docker pour rendre le projet déployable**

### **Étape 1.1 : Créer un fichier Dockerfile**

À la racine de votre projet, créez un fichier nommé `Dockerfile` :

```dockerfile
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
```

---

#### **Étape 1.2 : Créer un fichier `.dockerignore`**

Ajoutez un fichier `.dockerignore` pour éviter que Docker ne copie des fichiers inutiles dans l'image :

```raw
node_modules
dist
*.log
.env
```

---

#### **Étape 1.3 : Construire l’image Docker**

Dans le terminal, exécutez les commandes suivantes :

1. **Construire l'image Docker** :

   ```bash
   docker build -t plexsync .
   ```

2. **Vérifier que l’image est créée** :

   ```bash
   docker images
   ```

---

#### **Étape 1.4 : Exécuter le conteneur**

1. **Lancer l’application dans un conteneur Docker** :

   ```bash
   docker run --env-file .env -p 3000:3000 plexsync
   ```

2. **Vérifier le fonctionnement** :
   - L'application doit s'exécuter correctement et être accessible via les ports configurés (ex., 3000).

---

### **2. Ajouter des instructions dans le README**

Ajoutez un guide clair pour les développeurs qui souhaitent utiliser ou contribuer au projet. Voici un exemple de section pour le README :

---

#### **PlexSync**

PlexSync est un outil destiné à synchroniser les listes d'envies (wishlist) et les notes (ratings) entre Plex et d'autres services. Actuellement, il prend en charge SensCritique via son API GraphQL.

---

#### **Pré-requis**

- **Node.js** : Version 18 ou supérieure.
- **Docker** : Pour un déploiement simplifié (optionnel).
- **Compte SensCritique** avec identifiants.
- **Serveur Plex** avec un token API.

---

#### **Installation**

1. Clonez le projet :

   ```bash
   git clone https://github.com/votre-utilisateur/PlexSync.git
   cd PlexSync
   ```

2. Installez les dépendances :

   ```bash
   npm install
   ```

3. Configurez les variables d’environnement dans un fichier `.env` :

   ```raw
   SC_EMAIL=your_email@example.com
   SC_PASSWORD=your_password
   PLEX_IP=your_plex_server_ip
   PLEX_TOKEN=your_plex_api_token
   ```

4. Démarrez le projet :

   ```bash
   npm start
   ```

---

#### **Utilisation avec Docker**

1. Construisez l’image Docker :

   ```bash
   docker build -t plexsync .
   ```

2. Lancez le conteneur avec les variables d’environnement :

   ```bash
   docker run --env-file .env -p 3000:3000 plexsync
   ```

---

#### **Fonctionnalités**

- Synchronisation bidirectionnelle des listes d'envies entre Plex et SensCritique.
- Gestion des suppressions et ajouts.
- Synchronisation des notes Plex vers SensCritique (à venir).

---

#### **Contribuer**

1. Forkez le projet.
2. Créez une branche pour votre fonctionnalité :

   ```bash
   git checkout -b new-feature
   ```

3. Testez vos modifications.
4. Soumettez une pull request.

---

Avec ce guide, les développeurs et utilisateurs sauront comment configurer et exécuter votre projet, que ce soit localement ou via Docker.

---

### **3. Tests et finalisation**

1. Testez votre conteneur Docker pour vous assurer qu'il fonctionne dans divers environnements.
2. Partagez votre projet sur GitHub avec les instructions ajoutées.
3. Si besoin, configurez une intégration CI/CD (ex., avec GitHub Actions) pour automatiser la construction et le déploiement de l'image Docker.

Vous êtes prêt à partager votre outil ! Si vous avez besoin de personnaliser davantage cette configuration ou d’ajouter des fonctionnalités spécifiques, dites-le-moi. 😊

L'erreur indique que votre projet n'a pas de script `build` défini dans le fichier `package.json`. Le Dockerfile essaie d'exécuter `npm run build`, mais comme ce script n'existe pas, l'exécution échoue.

Voici comment résoudre ce problème :

---

### **1. Ajouter un script `build` dans `package.json`**

Le script `build` est généralement utilisé pour compiler des fichiers TypeScript vers JavaScript ou pour préparer le projet pour le déploiement.

#### Exemple de `package.json` avec un script `build`

Ouvrez votre fichier `package.json` et ajoutez ou modifiez la section `scripts` comme suit :

```json
{
  "name": "plexsync",
  "version": "1.0.0",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "ts-node-dev src/index.ts",
    "build": "tsc"
  },
  "dependencies": {
    "senscritique-graphql-api": "^1.0.0",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "typescript": "^4.5.0",
    "ts-node-dev": "^2.0.0"
  }
}
```

- **`build`:** Appelle `tsc` (TypeScript Compiler) pour compiler les fichiers TypeScript dans un dossier `dist`.
- **`start`:** Exécute l'application compilée.
- **`dev`:** Lance un serveur de développement.

---

### **2. Ajouter un fichier `tsconfig.json` (si absent)**

Le fichier `tsconfig.json` configure la compilation TypeScript. Si vous n’en avez pas, créez-le avec la commande suivante :

```bash
npx tsc --init
```

Puis, ajustez-le pour spécifier le répertoire de sortie (`dist`) :

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

---

### **3. Recompiler avec Docker**

Après avoir ajouté le script `build` et configuré TypeScript :

1. **Nettoyez les fichiers précédemment générés** :

   ```bash
   docker system prune -f
   ```

2. **Reconstruisez l’image Docker** :

   ```bash
   docker build -t plexsync .
   ```

---

### **4. Tester l’image Docker**

Lancez l’image pour vérifier qu’elle fonctionne :

```bash
docker run --env-file .env -p 3000:3000 plexsync
```

---

### **5. Validation**

- Si tout fonctionne, l’image Docker devrait être prête pour le déploiement.
- Si des erreurs subsistent, partagez les journaux pour une assistance plus spécifique. 😊
