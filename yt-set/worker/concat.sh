#!


concat="youtube_demo_1.ts|youtube_demo_2.ts|youtube_demo_3.ts|"
l=${#concat}
z=`expr $l - 1` 


#new_string=${concat:0:$z}"\""
new_string=${concat:0:$z}
echo $new_string

dir_command="$(pwd)"
OUTPUT="$(ls -la)"
echo "file list is: ${OUTPUT}"
echo "dir content is: ${dir_command}"