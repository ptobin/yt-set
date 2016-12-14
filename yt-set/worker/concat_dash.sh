#!


concat_command="pepe.mp1|pepe.mp2|"
stringlen=${#concat_command}
feo=$(echo $concat_command | awk -v var=$stringlen '{ concat_command=substr($0, 1, var - 1); print concat_command; }' )

echo $feo