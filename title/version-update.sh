#! /bin/sh
# Created Time: 2019-06-07 20:24:41
#

TITLE_FILE=./main.tex

git checkout ${TITLE_FILE}

cat ${TITLE_FILE} | while read line; do
    suffix=`echo ${line} | awk -F " " '{print $4}'`
    if [ "${suffix}" = "version" ]; then
        echo "find suffix = ${suffix}"

        #
        # get version
        #
        version=`echo ${line} | awk -F " " '{print $2}'`
        version=`echo ${version} | awk -F "}" '{print $1}'`
        echo "line = ${line}"
        echo "version = ${version}"

        MAJOR_VERSION=`echo ${version} | awk -F "." '{print $2}'`
        MINOR_VERSION=`echo ${version} | awk -F "." '{print $3}'`
        LAST_DATE=`echo ${version} | awk -F "." '{print $4}'`

        TODAY=`date +%m%d`

        echo "MAJOR_VERSION = ${MAJOR_VERSION}"
        echo "MINOR_VERSION = ${MINOR_VERSION}"
        echo "LAST_DATE = ${LAST_DATE}"
        echo "TODAY = ${TODAY}"

        #
        # check and generate new version string
        #
        MINOR_VERSION=$((MINOR_VERSION+1))

        if [ "${TODAY}" != ${LAST_DATE} ]; then
            MAJOR_VERSION=$((MAJOR_VERSION+1))
            MINOR_VERSION=0
        fi

        NEW_VERSION="0.${MAJOR_VERSION}.${MINOR_VERSION}.${TODAY}"

        SED_OPTION="s/${version}/${NEW_VERSION}/g"

        sed -i ${SED_OPTION} ${TITLE_FILE}

        #
        # update Total-commit-count
        #
        TOTAL_COMMIT_CNT=`echo ${line} | awk -F ":" '{print $2}'`
        TOTAL_COMMIT_CNT=`echo ${TOTAL_COMMIT_CNT} | awk -F "}" '{print $1}'`
        echo "TOTAL_COMMIT_CNT = ${TOTAL_COMMIT_CNT}"

        OLD_FOOTNOTE="Total-commit-count:${TOTAL_COMMIT_CNT}"

        TOTAL_COMMIT_CNT=$((TOTAL_COMMIT_CNT+1))
        NEW_FOOTNOTE="Total-commit-count:${TOTAL_COMMIT_CNT}"

        SED_OPTION="s/${OLD_FOOTNOTE}/${NEW_FOOTNOTE}/g"

        sed -i ${SED_OPTION} ${TITLE_FILE}
    fi
done

