# flush camera
for i in xrange(1,100):
  (success, frame) = camera.read() # capture image as array
  
# take photo
(success, frame) = camera.read() # capture image as array
raw = Image.fromarray(frame)
BGR = raw.split()
B = BGR[0].getdata()
G = BGR[1].getdata()
R = BGR[2].getdata()

# Sum columns of image up
z = 0
for y in xrange(0,HEIGHT):
  for x in xrange(0,WIDTH):
    denominator = float(R[z] + B[z])
    numerator = float(10*G[z])
    if denominator == 0:
      denominator = 1 # don't divide by zero
    columns[x] += numerator / denominator
    z += 1 # index in sequence
    
# Draw line
greener = numpy.mean(columns)
for x in xrange(0,WIDTH):
  if (columns[x] > greener):
    columns[x] = 1
    for y in xrange(0,HEIGHT):
      raw.putpixel((x,y), (254,254,254))
  else:
    columns[x] = 0

# Find objects
i = 0
start = 0
end = 0
objects = []
while (i < WIDTH):
  if (columns[i] == 1):
    start = i
    while (columns[i] == 1):
      i += 1
    end = i
    objects.append(start,end)
  else:
    i += 1
  
# Display
raw.save("RAW.jpg", "JPEG")
p = subprocess.Popen(["display", "RAW.jpg"])
time.sleep(1) # delays for 1 second
p.kill()
