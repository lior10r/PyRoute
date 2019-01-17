#!/usr/bin/env sh

# Paths
export PYROUTE_ENV=$(grub-mkrelpath $(dirname $0))
export PYROUTE_SRC_DIR=$PYROUTE_ENV/src
export PYROUTE_STAGE_DIR=$PYROUTE_ENV/stages
export PYROUTE_STAGE_FILE=$PYROUTE_ENV/.stage


function stage_down
{
    $PYROUTE_STAGE_DIR/$1/down.sh
}

function stage_up
{
    $PYROUTE_STAGE_DIR/$1/up.sh
}

function stage_connect
{
    $PYROUTE_STAGE_DIR/$1/connect.sh $2
}

function validate_stage
{
    stage=$1
    stage_fullpath=$PYROUTE_STAGE_DIR/$stage

    if ! [ -d $stage_fullpath ]; then
        echo "Stage \`$stage' not found."
        return -1
    fi

    if ! [ -x $stage_fullpath/up.sh -a \
           -x $stage_fullpath/down.sh ]; then
        echo "No scripts found for stage \`$stage'."
        return -1
    fi
}

function pyroute-stage-start
{
    stage=$1

    validate_stage $stage

    if [ $? -ne 0 ]; then
        return -1
    fi

    # Stop last stage if it's different than the new one
    if [ -f $PYROUTE_STAGE_FILE ]; then
        if [ $stage != $(cat $PYROUTE_STAGE_FILE) ]; then
            stage_down $(cat $PYROUTE_STAGE_FILE)
        fi
    fi

    stage_up $stage

    # Save stage
    echo $stage > $PYROUTE_STAGE_FILE
}

function pyroute-stage-stop
{
    if ! [ -f $PYROUTE_STAGE_FILE ]; then
        echo "No stage running at the moment..."
        return -1
    fi

    stage_down $(cat $PYROUTE_STAGE_FILE)

    # Delete stage file
    rm $PYROUTE_STAGE_FILE
}

function pyroute-connect
{
    service=$1

    if ! [ -f $PYROUTE_STAGE_FILE ]; then
        echo "No stage running at the moment..."
        return -1
    fi

    stage_connect $(cat $PYROUTE_STAGE_FILE) $service
}


# Export
export -f pyroute-stage-start
export -f pyroute-stage-stop
export -f pyroute-connect
