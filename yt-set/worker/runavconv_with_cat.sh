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
concat_command=" "
for segment in $segments
do
    echo "> segment is [$segment]"
	start=$(echo $segment | cut -f1 -d'-')
	duration=$(echo $segment | cut -f2 -d'-')
	
    echo "> start is [$start]"
    echo "> duration is [$duration]"
	out_file=$file"_$((i+=1)).ts"
	echo "> outfile   [$out_file]"
	concat_command=$concat_command$out_file" "
	echo "> concat_command   [$concat_command]"
	
    #command="avconv -ss " $start" -i "$2 "-t "$duration "-vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y "$out_file
	a="avconv -ss "
	b=$start
	c=" -i "
	d=$fullFileName 
	e=" -t "
	f=$duration 
#	g=" -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y "
	g=" -vcodec libx264 -acodec aac -f mpegts -strict experimental -y "
	h=$out_file
	cmd=$a$b$c$d$e$f$g$h
	
	echo "        SPLIT command: in loop[$i] BEGIN $cmd"
	eval $cmd
	echo "        SPLIT command: in loop [$i] END $cmd"
	
done
parts_file_name=$file"_parts.ts"
cat_command="cat "$concat_command" > "$parts_file_name
echo $cat_command
eval $cat_command
#cat youtube_demo_1.ts youtube_demo_1.ts youtube_demo_1.ts > youtube_demo_parts.ts

#avconv -i youtube_demo_parts.ts  -loglevel debug -acodec copy -ar 44100 -ab 96k -coder ac -bsf:v h264_mp4toannexb -y  youtube_demo_edited.mp4


newFile=$file"_edited.mp4"
echo "newFile"
echo $newFile
echo "about to create resulting file" $newFile
aa="avconv -i "
bb=$parts_file_name
#cc=" -loglevel debug -acodec copy -ar 44100 -ab 96k -coder ac -bsf:v h264_mp4toannexb -y "
cc=" -loglevel debug -acodec copy -ar 44100 -ab 96k -coder ac -y "
dd=$newFile

echo $aa
echo $bb
echo $cc
echo $dd

transcode_command=$aa$bb$cc$dd

echo "        MERGE command:  BEGIN $transcode_command"
eval $transcode_command
echo "        MERGE command:  END $transcode_command"

#avconv -i concat:$concat_command2 -c copy -bsf:a aac_adtstoasc -y $newFile
echo "******    ******    about to create resulting file $newFile finished"

mv $newFile ..
cd ..
#rm -r $file
#avconv -ss 3 -i $1 -t 5 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file1.ts
#avconv -ss 10 -i $1 -t 4 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file2.ts
#avconv -ss 17 -i $1 -t 5 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file3.ts

#avconv -i concat:"file3.ts|file2.ts|file1.ts" -c copy -bsf:a aac_adtstoasc -y full.mp4