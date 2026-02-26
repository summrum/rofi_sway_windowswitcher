#!/bin/sh
# Rofi sway window switcher mode v1.1

tmp_dir="${TMPDIR:-/tmp}"

get_windows() {
	count=0
	sep='<span'
	while IFS="$(printf '\t')" read -r winid urgent active wsid app_id data; do
		# Icon display hacks
		case "$app_id" in
			dev.*|org.*)
				icon="$app_id"
			;;
			signal)
				icon="$app_id-desktop"
			;;
			*)
				icon=$(printf '%s\n' "$app_id" | tr '[:upper:]' '[:lower:]')
			;;
		esac
		# Workspace display hacks
		[ -z "$wsid" ] && continue
	    case "$wsid" in
	        __i3_scratch)
	            wsid='[-]'
	            count=$((count+1))
	        ;;
	        *"$sep"*)
	            wsid="[${wsid%%"$sep"*} ]"
	        ;;
	        *)
	            wsid="[$wsid]"
	        ;;
	    esac
		printf '%s %s %s\000icon\037%s\037info\037%s\037urgent\037%s\037active\037%s\n' \
		"$wsid" "$app_id -" "$data" "$icon" "$winid" "$urgent" "$active"
		if [ "$count" -ge 2 ] && [ ! -f "$tmp_dir"/scratch ]; then
			touch "$tmp_dir"/scratch
		fi
	done << EOF
$(swaymsg -t get_tree | jq -r ' .. 
	| (.nodes? // empty)[]
	| select(.type == "workspace") as $ws
	| .nodes[], .floating_nodes[]
	| ..
	| objects
	| select(.app_id != null or .window_properties.class != null)
	| [ .id, .urgent, .focused, $ws.name, (.app_id // .window_properties.class), .name ]
	| @tsv ')
EOF
}

kill_scratched() {
	while IFS= read -r id; do
		[ -n "$id" ] && swaymsg "[con_id=$id] kill" >/dev/null
	done << EOF
$(swaymsg -t get_tree | jq -r ' .. 
	| objects 
	| select(.scratchpad_state? // "none" 
	| . != "none") 
	| .id ')
EOF
}

case ${ROFI_RETV:-0} in
	0)
		if command -v jq >/dev/null 2>&1; then
			get_windows
			if [ -f "$tmp_dir"/scratch ]; then
				printf '%s\n' "[ALL SCRATCHPAD WINDOWS]"
				rm "$tmp_dir"/scratch
			fi
		else
			printf '%s\n' "jq not found"
		fi
	;;
	1)	
	    case "$@" in
	    	"[ALL SCRATCHPAD WINDOWS]")
	    		swaymsg "[floating] scratchpad show" >/dev/null
	    		exit
	    	;;
	    	"jq not found")
	    		exit 1
	    	;;
	    	*)
	    		swaymsg "[con_id=${ROFI_INFO}] focus" >/dev/null
	    		exit
	    	;;
	    esac
	;;
	3)
		case "$@" in
		   	"[ALL SCRATCHPAD WINDOWS]")
		   		kill_scratched
		   		sleep 0.2
		   		get_windows
		   	;;
		   	"jq not found")
		   		exit 1
		   	;;
		   	*)
		   		swaymsg "[con_id=${ROFI_INFO}] kill" >/dev/null
		   		sleep 0.2
		   		get_windows
		   	;;
		esac	
	;;
esac
