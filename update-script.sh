#!/bin/sh

update_script() {
	update="$(curl -A "$agent" -s "$flixcli")"
	update="$(printf "%s\n" "$update" | diff -u "$script" -)"
	if [ -z "$update" ] ; then
		printf "script is up to date.\n"
	else
		if printf "%s\n" "$update" | patch "$script" - ; then
			printf "script has been updated\n"
		else
			printf "cant update for some reason\n"
		fi
	fi
}

flixcli="https://raw.githubusercontent.com/DemonKingSwarn/flix-cli/master/flix-cli.py"
agent="Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
script="./flix-cli.py"

update_script
