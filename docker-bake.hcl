variable "TAG" {
    default = "latest"
}

group "default" {
    targets = ["app"]
}

target "app" {
    context = "."
    dockerfile = "Dockerfile"
    tags = ["theraphael0000/clapclap:${TAG}"]
    platforms = ["linux/amd64", "linux/arm64"]
    output = ["type=registry"]
}