UID := $(shell id -u)
GID := $(shell id -g)

COMPOSE_CMD := LOCAL_UID=$(UID) LOCAL_GID=$(GID) docker compose

up:
	$(COMPOSE_CMD) up -d

down:
	$(COMPOSE_CMD) down

down-v:
	$(COMPOSE_CMD) down -v

ps:
	$(COMPOSE_CMD) ps
