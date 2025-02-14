prepare:
	pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

run:
	python -m src.bot

docker:
	docker compose build && docker compose up -d

get_cert:
	docker run -it --rm --name xray-core ghcr.io/xtls/xray-core 'x25519'