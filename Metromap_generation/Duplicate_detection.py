import os

def remove_duplicates(filepath):
    counter = 0
    while len(os.listdir(filepath)) != counter + 1:
        if counter % 100 == 0:
            print(counter)
        dir = os.listdir(filepath)
        file1split = dir[counter].split('_')
        for j in range(len(dir) - 1, counter - 1, -1):
            file2split = dir[j].split('_')
            if (file1split[-1] == file2split[-1] and file1split[-2] == file2split[-2] and dir[counter] != dir[j]):
                #print('filename1: ' + filepath + '/' + filename1)
                print('filename2: ' + filepath + '/' + str(j))
                os.remove(filepath + '/' + dir[j])
        counter += 1
remove_duplicates('Processed_news')#Processed_news