docker rmi syukurdocker/thermal_printer
#docker buildx build --platform linux/amd64,linux/arm64 --push -t syukurdocker/thermal_printer:latest .
BUILDER=$(docker buildx create --use)
docker buildx build --platform=linux/arm64 --push -t syukurdocker/thermal_printer:latest .
docker buildx rm $BUILDER
