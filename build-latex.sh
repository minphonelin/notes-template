#! /bin/sh
# Created Time: 2019-05-19 23:08:03
#

#
# ./build-latex.sh all  -> build all tex file and gen a full pdf file
# ./build-latex.sh      -> build changed tex file and gen a cache pdf file
#

#
# copy pdf to OUTPUT_DOC_DIR
#
OUTPUT_DOC_DIR=`pwd`

CMD="xelatex -halt-on-error "

TRUE=1
FALSE=0
START=`date +%s%N`
bBuildAll=${FALSE}
NOTES_CACHE_DIR=/tmp/notes-cache

#
# version update
#
CURRENT_DIR=`pwd`
cd ./title
./version-update.sh
cd ${CURRENT_DIR}

if [ "$#" != '0' ]; then
    echo
    echo "$0 $1"
    echo
    if [ "$1" = "all" ]; then
        bBuildAll=${TRUE}
    fi
fi

echo
echo "param $1"
echo "bBuildAll = ${bBuildAll}"
echo

if [ ${FALSE} -eq ${bBuildAll} ]; then
    ./cache-build.py
    if [ ! -d ${NOTES_CACHE_DIR} ]; then
        echo
        echo "[I] no update any Tex files"
        echo
        exit 0
    fi
    cd ${NOTES_CACHE_DIR}
fi

${CMD}notes.tex

if [ ${FALSE} -eq ${bBuildAll} ]; then
    if [ "$?" = "0" ]; then
        ${CMD}notes.tex # second build
    fi
fi

END=`date +%s%N`

if [ "$?" = "0" ]; then
    if [ -d ${OUTPUT_DOC_DIR} ]; then

        TARGET=notes.pdf
        if [ ${FALSE} -eq ${bBuildAll} ]; then
            TARGET=notes-cache.pdf
            cp ./notes.pdf notes-cache.pdf
            cp ./notes-cache.pdf ${OUTPUT_DOC_DIR}
        else
            cp ./notes.pdf ${OUTPUT_DOC_DIR}
        fi

        if [ "$?" = "0" ]; then
            echo "cp ${TARGET} to ${OUTPUT_DOC_DIR} success !"
        else
            echo "cp ${TARGET} to ${OUTPUT_DOC_DIR} fail !"
        fi
    else
        echo "no found dir : ${OUTPUT_DOC_DIR}"
    fi
fi

cd ${CURRENT_DIR}

COST=$((END-START))
COST_MS=`expr ${COST} / 1000000`
echo "COST_MS = ${COST_MS}"
COST_S=`awk 'BEGIN{printf "%.3f\n", ('$COST_MS'/1000)}'`
echo "build cost ${COST_S} s"

