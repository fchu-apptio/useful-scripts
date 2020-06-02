#!/bin/bash

ps aux | grep -i fort | awk '{print $2}' | xargs sudo kill -9
