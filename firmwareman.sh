#!/usr/bin/env bash

error=()
homedir=$(dirname $(pwd))
echo "$homedir"

function compilefw {
	echo "compiling $oldfwdir"
	sketch=$(basename $oldfwdir)
	echo "working on $sketch sketch"
	make -C $oldfwdir
	exstat=$?
	echo "exstat = $exstat"
	if [ "$exstat" = "0" ]; then 
		echo "compile successful"
		error+=(0)
	else
		echo "compile not successful"
		error+=(1)
	fi
}

function update {
	cp -r $newfw $(dirname $oldfw)
	rm -r $oldfw
}

function errorcatch {
	errorcount=0
	if [ "$host" = "linux" ]; then
		for e in ${error[@]}; do
			case $e in
				"0" ) echo "operation success";;
				"1" ) echo "error 1";;
				"2" ) echo "error 2";;
				"3" ) echo "error 3";;
			esac
			if [ "$e" != 0 ]; then
				errorcount=$((errorcount+1))
			else
				errorcount=$((errorcount+0))
			fi
		done
		if [ "$errorcount" -gt 0 ]; then
			echo "$errorcount errors occured"
			exit $errorcount
		else
			echo "no errors occured"
			exit 0
		fi
	fi
}

function fixlibraryreference {
	armflag=$(uname -m | grep -o arm)
		if [ ! -z "$armflag" ]; then
			if [ ! -f /usr/share/arduino/libraries/Wire/twi.h ] || [ ! -f /usr/share/arduino/libraries/Wire/twi.c ]; then
				echo "Fixing TWI library reference error"
				cp /usr/share/arduino/libraries/Wire/utility/* /usr/share/arduino/libraries/Wire
		fi
}

function firmwarecheck {
	fixlibraryreference
	if [ ! -d $homedir/data/sketches ]; then
		echo "Copying makefiles and compiling firmware"
		# http://askubuntu.com/questions/300744/copy-the-content-file-to-all-subdirectory-in-a-directory-using-terminal
		cp -r sketches $homedir/data/
		for oldfwdir in $homedir/data/sketches/*; do
			if [ oldfwdir != "libraries" ]:
				compilefw
		done
		error+=(0)
	else
		echo "Checking for firmware updates"
		for newfwdir in sketches/*; do
			nfwbasename=$(basename $newfwdir)
			echo "checking $nfwbasename firmware"
			for newfw in $newfwdir/*; do
				nfirmware=$(basename $newfw)
				nfwmatch=$(echo $nfirmware | grep -i -o $nfwbasename)
				if [ ! -z "$nfwmatch" ]; then
					echo "$nfirmware found in $newfwdir"
					for oldfwdir in $homedir/data/sketches/*; do
						ofwbasename=$(basename $oldfwdir)
						for oldfw in $oldfwdir/*; do
							ofirmware=$(basename $oldfw)
							ofwmatch=$(echo $ofirmware | grep -i -o $ofwbasename)
							onfwmatch=$(echo $ofirmware | grep -i -o $nfwbasename)
							if [ ! -z "$ofwmatch" ] && [ ! -z "$onfwmatch" ]; then
								echo "$ofirmware found in $oldfwdir"
								echo "comparing $ofirmware to $nfirmware"
								if [ "$ofirmware" != "$nfirmware" ]; then
									onum=$(echo ${ofirmware//[A-Za-z^.]/})
									nnum=$(echo ${nfirmware//[A-Za-z^.]/})
									if [ ! -z "$onum" ]; then
										echo "updating $ofirmware to $nfirmware"
										if [ ! -z "$nnum" ]; then
											if [ $(echo "$onum") -lt $(echo "$nnum") ]; then
												echo "saving $newfw over $oldfw"
												update
												compilefw
											else
												# Downgrading firmware is not supported
												echo "ERROR: legacy firmware found in update repository"
												error+=(2)
											fi
										else
											echo "ERROR: firmware in update repository lacks version info"
											echo "INFO: saving $newfw over $oldfw"
											update
											compilefw
										fi
									else
										echo "ERROR: legacy firmware lacks version info"
										if [ ! -z "$nnum" ]; then
											echo "INFO: saving $newfw over $oldfw"
											update
											compilefw
										else
											echo "ERROR: firmware update lacks version info"
											echo "ERROR: firmware can't be updated"
											error+=(3)
										fi
									fi
								else
								echo "no update required for $ofwbasename"
								onfwmatch=
								ofwmatch=
								nfwmatch=
								error+=(0)
								fi
							fi
						done
					done
				fi
			done
		done
	fi
}

firmwarecheck
errorcatch