# Project Initialization Commands

The commands that were used to initialize the project.

1. `npm init -y`
1. `npm install typescript --save-dev`
1. `npx tsc --init`
1. `npm install senscritique-graphql-api`
    1. Seems like there are vulnerabilities, so I will try to fix them
1. `npm audit fix`
    1. Did not fix, so GPT advised to use add some code to package.json, I wont' do it just now. Let's see if the project works even with vulnerabilities.

        ```json
        "resolutions": {
        "jose": "^4.16.0"
        }

         ```

1. `npm install plex-api`
   1. Now there are 10 moderate severity vulnerabilities
1. `npm install graphql-request` pour écrire des requêtes GraphQL facilement
1. `npm install dotenv` pour gérer les variables d'environnement comme les clés API et mots de passe
1. `npm install ts-node-dev --save-dev` Utilise ts-node-dev (un outil utile pour le développement rapide).
1. `npm install jest ts-jest @types/jest --save-dev`
1. `npx ts-jest config:init`
