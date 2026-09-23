# Imagen oficial de Node.js
FROM node:20-alpine

# Directorio de trabajo
WORKDIR /app

# Copiar primero archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install --production

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 3000

# Comando para iniciar la API
CMD ["npm", "start"]