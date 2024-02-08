#!/bin/bash
{
    apt update
    apt upgrade -y
    apt autoremove
    apt clean
} || {
    echo "System updates failed"
    exit 1
}