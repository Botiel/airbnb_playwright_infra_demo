
install:
	@pip install --upgrade pip; \
	pip install -r requirements.txt; \
	playwright install; \
	echo ">>> Installed Requirements";

clean-requirements:
	@pip freeze > check_req.txt; \
	if [ -s ./check_req.txt ]; then pip uninstall -y -r check_req.txt; fi; \
	rm check_req.txt

clean:
	@if [ -d .pytest_cache/ ]; then rm -r .pytest_cache/; fi
	@if [ -d pytest_reports/ ]; then rm -r pytest_reports/; fi
	@clear

run-tests:
	@python pytest_runner.py


####################################################### DOCKER #########################################################
BASE_IMAGE := airbnb-playwright-base
TEST_IMAGE := airbnb-playwright-test
CONTAINER := playwright-airbnb

docker-clean: delete-container delete-test-image

docker-super-clean: delete-container delete-test-image delete-base-image

docker-new-container: delete-container delete-test-image test-image create-container start-container

base-image:
	docker build -t ${BASE_IMAGE} -f local.base.Dockerfile . ;

test-image:
	@docker build -t ${TEST_IMAGE} -f local.test.Dockerfile . ;

create-container:
	@docker create --name ${CONTAINER} ${TEST_IMAGE};

start-container:
	@docker start ${CONTAINER}

log-container:
	@docker exec -it ${CONTAINER} bash

delete-container:
	@ if [ -n "$$(docker ps -a | grep -w "${CONTAINER}")" ]; \
 	then docker rm --force ${CONTAINER}; \
	echo ">>> Deleted Container ${CONTAINER}"; fi

delete-test-image:
	@ if [ -n "$$(docker image ls | grep -w "${TEST_IMAGE}")" ]; \
 	then docker rmi --force ${TEST_IMAGE}; \
	echo ">>> Deleted Image ${TEST_IMAGE}"; fi

delete-base-image:
	@ if [ -n "$$(docker image ls | grep -w "${BASE_IMAGE}")" ]; \
 	then docker rmi --force ${BASE_IMAGE}; \
	echo ">>> Deleted Image ${BASE_IMAGE}"; fi

container-run-test:
	@docker start ${CONTAINER}
	@if docker cp pytest_configurations.py ${CONTAINER}:app/; then echo ">>> Copied file successfully" else exit 1; fi
	@docker exec ${CONTAINER} python3 pytest_runner.py