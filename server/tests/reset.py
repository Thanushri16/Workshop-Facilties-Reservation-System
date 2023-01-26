#clear preexisting data file.
file = open("data/data.txt","w")
file.close()

with open('tests/testingdata.txt','r') as firstfile, open('data/data.txt','a') as secondfile: 
    # read content from first file
    for line in firstfile:  
        # append content to second file
        secondfile.write(line)