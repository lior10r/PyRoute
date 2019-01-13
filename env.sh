#!/usr/bin/env sh

# Constants
stage_dir="stages"
stage_file=".stage"
stage_dir_abs=$(grub-mkrelpath $stage_dir)


function stage_down
{
    $stage_dir_abs/$1/down.sh
}

function stage_up
{
    $stage_dir_abs/$1/up.sh
}

function stage_connect
{
    $stage_dir_abs/$1/connect.sh $2
}

function validate_stage
{
    stage=$1
    stage_fullpath=$stage_dir_abs/$stage

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
    if [ -f $stage_file ]; then
        if [ $stage != $(cat $stage_file) ]; then
            stage_down $(cat $stage_file)
        fi
    fi

    stage_up $stage

    # Save stage
    echo $stage > $stage_file
}

function pyroute-stage-stop
{
    if ! [ -f $stage_file ]; then
        echo "No stage running at the moment..."
        return -1
    fi

    stage_down $(cat $stage_file)

    # Delete stage file
    rm $stage_file
}

function pyroute-connect
{
    service=$1

    if ! [ -f $stage_file ]; then
        echo "No stage running at the moment..."
        return -1
    fi

    stage_connect $(cat $stage_file) $service
}


# Export
export -f pyroute-stage-start
export -f pyroute-stage-stop
export -f pyroute-connect
