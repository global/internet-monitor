.PHONY: init build run stop urls help
.SILENT: init

init:
	@echo Installing loki docker plugin...
	docker plugin ls | grep loki > /dev/null || docker plugin install  grafana/loki-docker-driver:latest --alias loki --grant-all-permissions

build:
	docker-compose build

run:
	docker-compose up

stop:
	docker-compose down

urls:
	@echo "List of the services running"
	@echo ""
	@echo "Services:"
	@echo " Prometheus 	 		http://localhost:9090/"
	@echo " Grafana   			http://localhost:3000/ (admin:admin)"
	@echo " Internet Monitor		http://localhost:8000/metrics"
	@echo " cAdvisor			http://localhost:8080/"

help:
	@echo "This project assumes that you have python and pip installed."
	@echo ""
	@echo "Targets:"
	@echo " init 	 		install all dependencies for environment"
	@echo " build   		build all containers"
	@echo " run			Run all containers using docker-compose"
	@echo " stop			Run all containers using docker-compose"
	@echo " urls			List services URLs running on docker-compose"
	@echo " help			display this information"
