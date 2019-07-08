import os

def read_go_map(file_name):
    
    returnMatrix =[]
    try:
        game_map = open(file_name, "r")
    
        line = game_map.readline()
        #line = remove_spaces(line)
        #returnMatrix.append(line) 
        while line != "":
            
            print(line)
            line = remove_spaces(line)
            returnMatrix.append(line)
            line = remove_spaces(line)
            line = game_map.readline()
        return (returnMatrix)
     except Exception, e:
        print ("Can't find file :" +file_name)
        print (e)
        quit()

def remove_spaces(line):
    return_line = ""
    for i in range (0,len(line)):
        if line[i] ==" ":
            pass
        else:
            return_line = return_line+ line[i]
            print ("returnLine = "+return_line)
    return return_line
def make_txt(matrix):
    file = open("output.txt","w")
    for i  in range (0, len(matrix)):
                     line = matrix[i]
                     file.write(line)


def read_py_map(file_name):
    
    returnMatrix =[]
    game_map = open(file_name, "r")
    
    line = game_map.readline()
    #line = remove_spaces(line)
    #returnMatrix.append(line) 
    while line != "":
      
        print(line)
        line = add_spaces(line)
        returnMatrix.append(line)
       
        line = game_map.readline()
    return (returnMatrix)

def add_spaces(line):
    return_line =""
    for i in range (0,len(line)):
       return_line= return_line + line[i] + " "  
    return (return_line)







                     

def main():
    
    choise = input("1 = pyMap -> goMap(add spaces) \n 2 =goyMap -> pyMap (remove spaces) \n")

    if choise ==1:
        matrix = read_py_map("map.txt")
    if choise ==2:
        matrix = read_go_map("mapFile.txt")
        
    make_txt(matrix)

        
            


main()
