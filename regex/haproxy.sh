# Get total time in milliseconds elapsed between the accept and the last close
# of request with status 200
grep -i "<url_here>" haproxy.log | perl -ne 'print "$1\n" if ( m/\/(\d+) 200/ )'
