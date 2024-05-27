#!usr/bin/env/ bash
echo "running hatch fmt..."
hatch fmt
echo "running hatch run security:check..."
hatch run security:check
echo "running hatch run types:check..."
hatch run types:check