#!/bin/bash

SCREEN="DSI-1"
STATE=`xrandr -q | sed -n -e'/^'$SCREEN'/p' | awk '{print $5}'`
NEW_STATE="normal"

if [ "$STATE" != "inverted" ] ;
then
	NEW_STATE="inverted"
fi

xrandr --output $SCREEN --rotate $NEW_STATE
