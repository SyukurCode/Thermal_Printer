docker rmi syukurdocker/thermal_printer
#docker build -t syukurdocker/thermal_printer .
#docker push syukurdocker/thermal_printer
docker buildx build --platform linux/amd64,linux/arm64 --push -t syukurdocker/thermal_printer:latest .
