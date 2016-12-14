import json

seg_ori ="   segments =    [[    0 , 2 ],[ 4 , 6 ],[ 8 , 10 ] ]"
parts  = seg_ori.split("=")
list = json.loads(parts[1])
largo= len(list)
list_0=list[0]
print(list_0)
print(largo)
print(parts[0])