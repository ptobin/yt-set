#!
for i; do 
    echo $i 
 done

echo 'filename in $2 = ' $2
echo 'segments in $4 = ' $4
baseDir='/tmp'
fullFileName=$2
file=$(echo $fullFileName | cut -f1 -d'.') 
echo 'file = ' $file
echo 'baseDir = ' $baseDir

cd $baseDir
ls
mkdir $file
cd $file
ls
cp $baseDir"/"$fullFileName . 
ls

IN=$4

segments=$(echo $IN | tr "|" "\n")
i=0
concat_command2=""
for segment in $segments
do
    echo "> segment is [$segment]"
	start=$(echo $segment | cut -f1 -d'-')
	duration=$(echo $segment | cut -f2 -d'-')
	
    echo "> start is [$start]"
    echo "> duration is [$duration]"
	out_file=$file"_$((i+=1)).ts"
	echo "> outfile   [$out_file]"
	concat_command2=$concat_command2$out_file'\|'
	echo "> concat_command2   [$concat_command2]"
	
    #command="avconv -ss " $start" -i "$2 "-t "$duration "-vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y "$out_file
	a="avconv -ss "
	b=$start
	c=" -i "
	d=$fullFileName 
	e=" -t "
	f=$duration 
	g=" -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y "
	h=$out_file
	cmd=$a$b$c$d$e$f$g$h
	
	echo "        SPLIT command: in loop[$i] BEGIN $cmd"
	eval $cmd
	echo "        SPLIT command: in loop [$i] END $cmd"
	
done

l=${#concat_command2}
echo "l is"
echo $l
z=`expr $l - 1` 
echo "z is"
echo $z

#new_string=${concat_command2:0:$z}
temp_concat=${concat_command2%?}
new_string=${temp_concat%?}
full_concat="\""$new_string"\""
echo "new concat command is"
echo $full_concat


newFile=$file"_edited.mp4"
echo "newFile"
echo $newFile
echo "about to create resulting file" $newFile
aa="avconv -i concat:"
bb=$full_concat
cc=" -loglevel debug -c copy -bsf:a aac_adtstoasc -y "
dd=$newFile
ee="youtube_demo_art_edited.mp4"

echo $aa
echo $bb
echo $cc
echo $dd

cmd_2=$aa$bb$cc$dd

echo "        MERGE command:  BEGIN $cmd_2"
eval $cmd_2
echo "        MERGE command:  END $cmd_2"

#avconv -i concat:$concat_command2 -c copy -bsf:a aac_adtstoasc -y $newFile
echo "******    ******    about to create resulting file $newFile finished"

#mv $newFile ..
#cd ..
#rm -r $file
#avconv -ss 3 -i $1 -t 5 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file1.ts
#avconv -ss 10 -i $1 -t 4 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file2.ts
#avconv -ss 17 -i $1 -t 5 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file3.ts

#avconv -i concat:"file3.ts|file2.ts|file1.ts" -c copy -bsf:a aac_adtstoasc -y full.mp4