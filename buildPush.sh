#!/bin/bash
docker buildx build --platform linux/arm64 -t guestros/simple-python-scheduler:latest --push .