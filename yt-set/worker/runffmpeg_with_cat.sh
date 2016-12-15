#!
echo 'runffmpeg_with_cat.sh invoked with'
for i; do 
    echo $i 
done

baseDir='/tmp'
fullFileName=$2
file=$(echo $fullFileName | cut -f1 -d'.') 
extension='.ts'
echo 'filename in $2 = ' $2
echo 'segments in $4 = ' $4
echo 'file = ' $file
echo 'baseDir = ' $baseDir

cd $baseDir
dir_command="$(pwd)"
echo "                dir content is: ${dir_command}"
OUTPUT="$(ls -la)"
echo "                file list is: ${OUTPUT}"
ls
mkdir $file

cd $file
dir_command="$(pwd)"
echo "                dir content is: ${dir_command}"
OUTPUT="$(ls -la)"
echo "                file list is: ${OUTPUT}"
ls
cp $baseDir"/"$fullFileName . 
ls
dir_command="$(pwd)"
echo "                dir content is: ${dir_command}"
OUTPUT="$(ls -la)"
echo "                file list is: ${OUTPUT}"
IN=$4

segments=$(echo $IN | tr "|" "\n")
i=0
concat_command=""
for segment in $segments
do
    echo "> segment is [$segment]"
	start=$(echo $segment | cut -f1 -d'-')
	duration=$(echo $segment | cut -f2 -d'-')
	
    echo "> start is [$start]"
    echo "> duration is [$duration]"
	out_file=$file"_$((i+=1))"$extension
	echo "> outfile  [$out_file]"
	concat_command=$concat_command$out_file"|"
	echo "> concat_command   [$concat_command]"
	
	#ffmpeg -ss 00:00:05 -t 6 -i input.mov -vcodec copy -acodec copy output.mov
	#ffmpeg -ss <start> -t <duration> -i in1.avi -vcodec copy -acodec copy out1.avi

	
	
	a="/usr/bin/ffmpeg -ss "
	b=$start
	c=" -i "
	d=$fullFileName 
	e=" -t "
	f=$duration 
	#g=" -vcodec copy -acodec copy "
	g=" -loglevel debug -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -y "
	h=$out_file
	cmd=$a$b$c$d$e$f$g$h
	
	echo "        SPLIT command: in loop[$i] BEGIN $cmd"
	eval $cmd
	echo "        SPLIT command: in loop [$i] END $cmd"
	dir_command="$(pwd)"
	echo "                dir content is: ${dir_command}"
	OUTPUT="$(ls -la)"
	echo "                file list is: ${OUTPUT}"
done

stringlen=${#concat_command}
new_concat_command=$(echo $concat_command | awk -v var=$stringlen '{ concat_command=substr($0, 1, var - 1); print concat_command; }' )

echo $new_concat_command

newFile=$file"_edited.mp4"
echo "newFile"
echo $newFile
echo "about to create resulting file" $newFile
parts_file_name=$file"_parts.ts"
cat_command="/usr/bin/ffmpeg -i \"concat:$new_concat_command\" -c copy -bsf:a aac_adtstoasc "$newFile
echo "about to call ffmpeg concat with: "$cat_command
eval $cat_command
#cat youtube_demo_1.ts youtube_demo_1.ts youtube_demo_1.ts > youtube_demo_parts.ts
dir_command="$(pwd)"
echo "                dir content is: ${dir_command}"
OUTPUT="$(ls -la)"
echo "                file list is: ${OUTPUT}"
mv $newFile ..
cd ..
#rm -r $file
#avconv -ss 3 -i $1 -t 5 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file1.ts
#avconv -ss 10 -i $1 -t 4 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file2.ts
#avconv -ss 17 -i $1 -t 5 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y file3.ts

#avconv -i concat:"file3.ts|file2.ts|file1.ts" -c copy -bsf:a aac_adtstoasc -y full.mp4