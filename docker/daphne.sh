#!/bin/sh
#make collectstatic
/usr/local/bin/daphne edem.asgi:channel_layer -b 0.0.0.0 -p 6000 --root-path=/app
