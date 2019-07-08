BACKEND_FOLDER=backend
FRONTEND_FOLDER=frontend
BACKEND_FLAGS =

client:
	cd ${FRONTEND_FOLDER}; \
	python2 cap_man.py

server:
	cd ${BACKEND_FOLDER}; \
	go run ${BACKEND_FLAGS} *.go

server-debug: BACKEND_FLAGS = -race
server-debug: server

clean:
	find -name *.pyc | xargs rm -f
