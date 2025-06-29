
# EcoDeliver

**EcoDeliver** je backend aplikacija razvijena kao rješenje za logističku podršku i slanje paketa za mala poduzeća. Projekt je podijeljen u više servisa i svi su dokerizirani radi lakšeg pokretanja i postavljanja.

## 📦 Glavne komponente

Aplikacija se sastoji od tri servisa:

- `auth-service` – registracija i prijava korisnika
- `driver-service` – upravljanje vozačima i njihovim podacima
- `tracking-service` – praćenje lokacije vozača u stvarnom vremenu

Svaki servis je izgrađen pomoću **FastAPI**, a za bazu podataka koristi se **AWS DynamoDB**.

## 🧪 Tehnologije

- Python 3.11
- FastAPI
- AWS DynamoDB
- Docker
- Docker Compose
- Nginx (kao load balancer)

## ⚙️ Pokretanje aplikacije

### Preduvjeti

- Docker i Docker Compose
- Git

### Koraci

```bash
git clone https://github.com/senadmustafi/EcoDeliver.git
cd EcoDeliver
docker-compose up --build
```
### 📁Struktura
```bash
EcoDeliver/
├── auth-service/
│   ├── main.py
│   ├── .env.dist
│   ├── Dockerfile
│   └── requirements.txt
├── driver-service/
│   ├── main.py
│   ├── .env.dist
│   ├── Dockerfile
│   └── requirements.txt
├── tracking-service/
│   ├── main.py
│   ├── .env.dist
│   ├── Dockerfile
│   └── requirements.txt
├── config/
│   └── nginx-proxy.conf
├── docker-compose.yml
├── .env.dist
└── README.md
```
### 🐳Dockerfile (Slični za svaki servis)
```bash
FROM  python:3.12
WORKDIR  /usr/src/app
ADD  main.py  requirements.txt  .
RUN  pip  install  -r  requirements.txt
CMD  ["python",  "-m",  "uvicorn",  "main:app",  "--host",  "0.0.0.0",  "--port",  "8000"]
```
### 🐳docker-compose.yml 
```bash
services:
	auth:
		build:
			context: ./auth-service

		env_file:
			- .env

	delivery:
		build:
			context: ./delivery-service
		env_file:
			- .env

 
	driver-tracking:
		build:
			context: driver-tracking-service
		env_file:
			- .env
		proxy:
			image: nginx:1.29-alpine
			volumes:
			- ./config:/etc/nginx/conf.d:ro
		ports:
			- 12345:80
```
### 🌐 Nginx konfiguracija
```bash
server{
	listen 80 default_server;
	server_name _;


	location /auth/
	{
		proxy_pass http://auth:8000/;

		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}


	location /delivery/
	{
		proxy_pass http://delivery:8000/;

		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}

	location /drivers
	{
		return 302 /drivers/;
	}

	location /drivers/
	{
		proxy_pass http://driver-tracking:8000/;

		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}
}

```
