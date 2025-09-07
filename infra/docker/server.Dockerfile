FROM node:18
WORKDIR /usr/src/app
COPY package.json pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/server ./apps/server
RUN npm install -g pnpm && pnpm install --filter @parkcap/server...
CMD ["pnpm","--filter","@parkcap/server","dev"]
