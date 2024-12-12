# PlexSync


## Compiling & Deploying

Commands to compile the project

## Normal Compile

1. `npm run build` - Compiles npm
1. `node dist/index.js` - Deploys and runs

### Normal Compile using Docker

1. `npm run build` - Compiles npm
1. `docker build -t plexsync .` - compiles docker image
1. `docker run --env-file .env -p 3000:3000 plexsync` - deploys and runs docker image

### Clean recompiling after errors

1. `rd -r "dist"`
1. `npm run build`
1. `docker system prune -f`
1. `docker build -t plexsync .`
1. `docker run --env-file .env -p 3000:3000 plexsync`