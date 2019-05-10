
first-run:
	cd docker && ./build-base.sh
	docker-compose up --build django
