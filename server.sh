#!/bin/bash

# conda activate python36

# python pos_ner_server.py
# python address_format_server.py

nohup python pos_ner_server.py &
nohup python address_format_server.py &