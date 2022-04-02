#! /bin/bash
# Created Time: 2019-06-28 06:46:54
#

GIT_CMDS=(
    "git diff "
    "git format-patch HEAD~"
    "git log --pretty=oneline  -1"
    "git config --get user.email"
)

GetCommitVersion()
{
    GIT_DIFF_TITLE=.diff-title
    COMMIT_VERSION=

    ${GIT_CMDS[0]} ./title/ > ${GIT_DIFF_TITLE}

    if [ -f ${GIT_DIFF_TITLE} ]; then

        while read line; do

            suffix=`echo ${line} | awk -F "%" '{print $2}'`
            if [ "${suffix}" = " version" ]; then
                version=`echo ${line} | awk -F "V" '{print $2}'`
                version=`echo ${version} | awk -F "}" '{print $1}'`
                COMMIT_VERSION=${version}
            fi
        done < ${GIT_DIFF_TITLE}

        rm ${GIT_DIFF_TITLE}
    fi

    if [ "${COMMIT_VERSION}" != "" ]; then
        echo "COMMIT_VERSION=${COMMIT_VERSION}"
    else
        exit 1
    fi
}

main()
{
    if [ 0 == $# ]; then
        echo "[Error] no input params"
        exit 1
    else
        case ${1} in
            "current-version") # get commit version
                GetCommitVersion
                ;;
            "patch")   # generate patch
                echo `${GIT_CMDS[1]}`

                REPO_NAME=${2}
                echo "REPO_NAME = ${REPO_NAME}"
                if [ ! -z "${REPO_NAME}" ]; then
                    PATCH=`ls *.patch`
                    PATCH=`echo ${PATCH} | awk -F "patch" '{print $1}'`
                    echo "PATCH = ${PATCH}"
                    mv ${PATCH}patch "${PATCH}${REPO_NAME}.patch"
                fi
                ;;
            "last-version-idx")# get last log
                VERSION_IDX=`${GIT_CMDS[2]} | awk -F "|" '{print $2}'`
                echo "VERSION_IDX=${VERSION_IDX}"
                ;;
            "email")   # get email info
                EMAIL=`${GIT_CMDS[3]}`
                echo "EMAIL=${EMAIL}"
                ;;
            "GitAdd")  # git add 
                git add -u .
                git add .
                ;;
        esac
    fi
}

main $*

