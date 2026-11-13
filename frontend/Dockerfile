FROM node:22-alpine

WORKDIR /app

# Copia los archivos de configuración
COPY package*.json ./

# Instala las dependencias limpias dentro de la imagen
RUN npm install

# Copia el resto del código fuente
COPY . .

EXPOSE 4200

# Comando para iniciar el servidor de desarrollo de Angular
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll=2000"]