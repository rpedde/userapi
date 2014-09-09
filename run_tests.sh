#!/bin/bash

WHAT=${1:-nose}

case "${WHAT}" in
    nose)
        nosetests -v $(dirname $0)/tests/*test*.py
        ;;
    pep8)
#        pep8 --repeat --show-pep8 --show-source $(dirname $0)/userapi
        pep8 $(dirname $0)/userapi
        pyflakes $(dirname $0)/userapi
        ;;
esac
