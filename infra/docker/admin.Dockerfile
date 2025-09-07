FROM node:18
WORKDIR /usr/src/app
COPY package.json pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/admin ./apps/admin
RUN npm install -g pnpm && pnpm install --filter @parkcap/admin...
CMD ["pnpm","--filter","@parkcap/admin","dev"]
