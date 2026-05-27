variable "DOCKERHUB_USERNAME" {
  default = ""
}

group "default" {
  targets = ["backend", "frontend"]
}

target "backend" {
  context    = "."
  dockerfile = "Dockerfile"
  target     = "backend-stage"
  tags       = ["${DOCKERHUB_USERNAME}/bias-auditor-api:latest"]
  cache-from = ["type=gha"]
  cache-to   = ["type=gha,mode=max"]
}

target "frontend" {
  context    = "."
  dockerfile = "Dockerfile"
  target     = "frontend-stage"
  tags       = ["${DOCKERHUB_USERNAME}/bias-auditor-ui:latest"]
  cache-from = ["type=gha"]
  cache-to   = ["type=gha,mode=max"]
}
