# bento robot bento-box-neo bashrc


BLACK="\e[90;47m" #offline (bright black fg; dull white bg)
RED="\e[31;1;5m" #shieet (red fg ; bold ; blinking)
YELLOW="\e[33;1m" #uh-oh (yellow fg)
GREEN="\e[32m" #ok
MAGENTA="\e[35m" #looks cool
RESET="\e[0m" #clear effects



# Function: choose_color_by_threshold <number> <threshold1> <colorVar1> [<threshold2> <colorVar2> ...]
choose_color_by_threshold() {
  local num="$1"; shift
   while (( $# )); do
    local threshold="$1"; shift
    local color="$1"; shift

    # Numeric compare: if num > threshold then print color and return success
    # Support integer and floating by using awk comparison
    if awk -v n="$num" -v t="$threshold" 'BEGIN{exit(!(n>t))}'; then
      printf '%s' "$color"
      return 0
    fi
  done

  # No match: return empty and non-zero status
  printf ''
  return 1
}


##### Hostname banner

lolcat << EOF

__________               __           __________                _______
\______   \ ____   _____/  |_  ____   \______   \ _______  ___  \      \   ____  ____
 |    |  _// __ \ /    \   __\/  _ \   |    |  _//  _ \  \/  /  /   |   \_/ __ \/  _ \\
 |    |   \  ___/|   |  \  | (  <_> )  |    |   (  <_> >    <  /    |    \  ___(  <_> )
 |______  /\___  >___|  /__|  \____/   |______  /\____/__/\_ \ \____|__  /\___  >____/
        \/     \/     \/                      \/            \/         \/     \/
EOF



##### System info

# get processors
                 # "model name" on non-raspi
PROCESSOR_NAME=$(grep "Model" /proc/cpuinfo | cut -d ' ' -f3- | awk '{print $0}' | head -1)
PROCESSOR_COUNT=$(getconf _NPROCESSORS_ONLN)

echo -e "
${RESET}\e[1msystem info:
$RESET  Distro......: $RESET$(cat /etc/*release | grep "PRETTY_NAME" | cut -d "=" -f 2- | sed 's/"//g')
$RESET  Kernel......: $RESET$(uname -sr)
$RESET  CPU.........: $RESET$PROCESSOR_NAME ($PROCESSOR_COUNT$RESET vCPU)$RESET"


##### Load info

# get percentual load averages
IFS=" " read -r CPU_LOAD1 CPU_LOAD5 CPU_LOAD15 <<<"$(cat /proc/loadavg | awk -v proc_count="$PROCESSOR_COUNT" '{print $1 * 100 / proc_count,  $2 * 100 / proc_count,  $3 * 100 / proc_count}')"
# get free memory
IFS=" " read -r MEM_USED MEM_AVAIL MEM_TOTAL <<<"$(free -th | grep "Mem" | awk '{print $3,$7,$2}')"
MEM_USED_PCT=$(echo "${MEM_USED::-2} ${MEM_TOTAL::-2}" | awk '{print $1 * 100 / $2}')

echo -e "
${RESET}\e[1mload info:
$RESET  Uptime......: $RESET$(uptime -p)
$RESET  Load.avg....: \
$(choose_color_by_threshold $CPU_LOAD1 100 $(echo -e ${RED}'(overloaded!) ') 90 $YELLOW 0 $GREEN)$CPU_LOAD1%$RESET (1m), \
$(choose_color_by_threshold $CPU_LOAD5 100 $(echo -e ${RED}'(overloaded!) ') 90 $YELLOW 0 $GREEN)$CPU_LOAD5%$RESET (5m), \
$(choose_color_by_threshold $CPU_LOAD15 100 $(echo -e ${RED}'(overloaded!) ') 90 $YELLOW 0 $GREEN)$CPU_LOAD15%$RESET (15m) \

$RESET  Memory......: \
$(choose_color_by_threshold $MEM_USED_PCT 90 $RED 70 $YELLOW 0 $GREEN)${MEM_USED} (${MEM_USED_PCT}%)$RESET used, \
${MEM_TOTAL}$RESET total\

$RESET"


##### Storage use

mapfile -t dfs < <(df -H -x zfs -x squashfs -x tmpfs -x devtmpfs -x overlay --output=target,pcent,size | tail -n+2)

echo -e "${RESET}\e[1mstorage use:$RESET"
for line in "${dfs[@]}"; do
    val=$(echo "${line}" | awk '{print $2}')
    color=$(choose_color_by_threshold ${val:0:-1} 90 $RED 70 $YELLOW 0 $GREEN)
    printf "  %-31s${color}%-3s${RESET} from %+4s\n" ${line}
done
echo "" # newline


##### Network IPs
# TODO


##### ROS2 nodes

# echo -e "${RESET}\e[1mros2 nodes:$RESET"
# ros2 node list
# echo "" # newline


##### Tips

echo -e "${RESET}\e[1mcommands:$RESET
$MAGENTA  Monitoring     :$RESET btop / htop
$MAGENTA  Git UI         :$RESET lazygit
$MAGENTA  Git login      :$RESET gh
$MAGENTA  Folder view    :$RESET tree
$MAGENTA  libcamera test :$RESET cam -l
$RESET"

