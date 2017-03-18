#!/usr/bin/env bash
docker build -t xerohige/chimecho .
docker run  --name "Chimecho" \
            --net="host" \
            -v $(pwd)/data/alerts:/chimecho/alerts \
            -v $(pwd)/data/rules:/chimecho/rules \
            -v $(pwd)/data/rules_templates:/chimecho/rules_templates \
            -p 8155:5000 \
            -p 1521:1521 \
            xerohige/chimecho sh -c "/chimecho/startServer.sh"
