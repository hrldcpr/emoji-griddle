input="$1"
output="${input%.png}-sm.png"

if [ ! -f $output ]; then
  # output doesn't exist yet, so go ahead and make it
  vips resize $input $output 0.25
fi
