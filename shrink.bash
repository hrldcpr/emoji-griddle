input="$1"
output="${input%.png}-sm.png"

if [ ! -f $output ]; then
  # output doesn't exist yet, so go ahead and make it
  vips thumbnail $input $output 134 --height 134 --size force
fi
