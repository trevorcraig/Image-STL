#!/usr/bin/python3

# Creating A perfect Mesh
# In order for this to work we need to find 3D space points
# Written By Trevor Craig
# Started on April 1, 2021

# Libraries
import numpy as np
from stl import mesh
import math
import sys
import time
import cv2

# Notes
# Can apply a scalor that might allow smoothing if it was bigger than needed
# Instead of cubes just make an overlay map.Might be a pain
# ORginally written all in numpy but that was slow to append to
# This now uses lists

# Extra Functions
def ResizeImage(FileName,scale_percent):
    img = cv2.imread(FileName, cv2.IMREAD_UNCHANGED)
    print('Original Dimensions : ',img.shape)
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    #Resized Image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    print('Resized Dimensions : ',resized.shape)
    #Return a gray scale image
    img = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    return(img)

# Print iterations progress
# Adapted From
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

# Classes 
class Timer:
    def __init__(self):
        self.starttime=time.time()
        self.lasttimechecked=time.time()
        
    def CheckTime(self):
        self.lasttimechecked=time.time()
        timeelapsed=self.lasttimechecked-self.starttime
        return(round(timeelapsed,2))
    
    def ResetTimer(self):
        self.starttime=time.time()
        self.lasttimechecked=time.time()
        
class DefinedCube:
    def __init__(self,Point1,Point2,Point3,Point4):
        # Define the 8 vertices of the cube
        # Eulers formula F+V-E=2
        # Face + Vertices-Edges=2
        # 6+8-Edges=2
        #Edges=12
        self.Point1=Point1
        self.Point2=Point2
        self.Point3=Point3
        self.Point4=Point4
        self.PlacePoint()
        
    def PlacePoint(self):
        self.vertices=[\
            [self.Point1.x,  self.Point1.y, 0],#0
            [self.Point2.x, self.Point2.y, 0],#1
            [self.Point3.x, self.Point3.y, 0],#2
            [self.Point4.x,  self.Point4.y, 0],#3
            [self.Point1.x,  self.Point1.y, self.Point1.z],#4
            [self.Point2.x,  self.Point2.y, self.Point2.z],#5
            [self.Point3.x,  self.Point3.y, self.Point3.z],#6
            [self.Point4.x,  self.Point4.y, self.Point4.z]]#7


        #This might actually be edges
        self.faces =[\
            [0,3,1],#0
            [1,3,2],#1
            [0,4,7],#2
            [0,7,3],#3
            [4,5,6],#4
            [4,6,7],#5
            [5,1,2],#6
            [5,2,6],#7
            [2,3,6],#8
            [3,7,6],#9
            [0,1,5],#10
            [0,5,4]]#11
        
    def AddtoFaces(self, value):
        returnfaces =[\
            [0+value,3+value,1+value],#0
            [1+value,3+value,2+value],#1
            [0+value,4+value,7+value],#2
            [0+value,7+value,3+value],#3
            [4+value,5+value,6+value],#4
            [4+value,6+value,7+value],#5
            [5+value,1+value,2+value],#6
            [5+value,2+value,6+value],#7
            [2+value,3+value,6+value],#8
            [3+value,7+value,6+value],#9
            [0+value,1+value,5+value],#10
            [0+value,5+value,4+value]]#11
        return(returnfaces)
        
# A point has x,y,z
# Maybe replace the numpy arrays with lists and only translate at the end
class Point:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
                        
class Assembly:
    def __init__(self):
        self.vertices=[]
        self.faces=[]
        self.NumberofAdditions=0
        
    def AddCube(self,Cube):
        if len(self.vertices)==0:
            self.faces=Cube.faces
            self.vertices=Cube.vertices
            self.NumberofAdditions=1
        else:
            #Each addition has 7 faces
            MaxValue=8*self.NumberofAdditions
            FacestoAdd=Cube.AddtoFaces(MaxValue)
            self.faces.extend(FacestoAdd)
            self.vertices.extend(Cube.vertices)
            self.NumberofAdditions=self.NumberofAdditions+1
            
    def MakeMesh(self):        
        numpyfaces=np.array(self.faces)
        numpyvertices=np.array(self.vertices)
        your_mesh = mesh.Mesh(np.zeros(numpyfaces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(numpyfaces):
            for j in range(3):
                your_mesh.vectors[i][j] = numpyvertices[f[j],:]
        self.Mesh=your_mesh
        
    def SaveMesh(self,Filename):
        # Write the mesh to file
        self.Mesh.save(Filename)
        
        
class ImagetoCad:
    def __init__(self,img,wantedwidth,wantedextrusion):
        self.img=img
        self.height = len(img)
        self.width = len(img[0])
        self.wantedwidth=wantedwidth
        self.scalor=wantedwidth/self.width
        self.wantedheight=self.height*self.scalor
        self.thickness=3 #Whatever I want Really This is the base layer it builds on
        self.wantedextrusion=wantedextrusion #Height off of the thickness
        
        self.GiantAssembly=Assembly()#PrepareTheAssembly
        print("MakingMesh")
        self.AssemblyPoints()
        self.GiantAssembly.MakeMesh()

            
    def AssemblyPoints(self):
        print("Starting!")
        LengthofProgressBar=50
        Clock=Timer()
        for rowval, rowelem in enumerate(self.img):
            printProgressBar(0, self.width, prefix = 'Progress:', suffix = 'Complete', length = LengthofProgressBar)
            for colval,colelem in enumerate(rowelem):
                #[Point1,Point2,Point3,Point4]=self.GetSquarePoints(rowval,colval,colelem)
                [Point1,Point2,Point3,Point4]=self.GetSmoothPoints(rowval,colval,colelem)
                NewCube=DefinedCube(Point1,Point2,Point3,Point4)
                self.GiantAssembly.AddCube(NewCube)   
                printProgressBar(colval + 1, self.width, prefix = 'Progress:', suffix = 'Complete', length = LengthofProgressBar)
                
            print(str(rowval)+"|"+str(self.height)+" in "+str(Clock.CheckTime())+" seconds\n")
            Clock.ResetTimer()


    def GetSquarePoints(self,rowval,colval,colelem):
        xlocal=rowval*self.scalor-self.wantedheight/2
        ylocal=colval*self.scalor-self.wantedwidth/2
        extrudheight=self.thickness+self.wantedextrusion*(colelem/256)

        Point1=Point(xlocal,ylocal,extrudheight)
        Point2=Point(xlocal+self.scalor,ylocal,extrudheight)
        Point3=Point(xlocal+self.scalor,ylocal+self.scalor,extrudheight)
        Point4=Point(xlocal,ylocal+self.scalor,extrudheight)
        return([Point1,Point2,Point3,Point4])
    
    def GetSmoothPoints(self,rowval,colval,colelem):
        xlocal=rowval*self.scalor-self.wantedheight/2
        ylocal=colval*self.scalor-self.wantedwidth/2
        extrudheight=self.thickness+self.wantedextrusion*(colelem/256)
        orginalheight=extrudheight
        Point1=Point(xlocal,ylocal,extrudheight)

        #None of this does corner checks but seems to look ok at the moment
        
        #Point 2 check
        if self.height>rowval+1: #height width
            colelem=self.img[rowval+1][colval]
            extrudheight=self.thickness+self.wantedextrusion*(colelem/256)
        else:
            extrudheight=orginalheight
        
        Point2=Point(xlocal+self.scalor,ylocal,extrudheight)

        # Point 3 Check
        if self.height>rowval+1: #height width
            if self.width>colval+1: #height width
                colelem=self.img[rowval+1][colval+1]
                extrudheight=self.thickness+self.wantedextrusion*(colelem/256)
            else:
                extrudheight=orginalheight
        Point3=Point(xlocal+self.scalor,ylocal+self.scalor,extrudheight)
        # Point 4 Check
        if self.width>colval+1: #height width
            colelem=self.img[rowval][colval+1]
            extrudheight=self.thickness+self.wantedextrusion*(colelem/256)
        else:
            extrudheight=orginalheight
            
        Point4=Point(xlocal,ylocal+self.scalor,extrudheight)
        
        return([Point1,Point2,Point3,Point4])           
        
        
def main():
    ProgramTimer=Timer()
    #Load in new file
    reductepercntage=100 #Larger is better quality images 0-100, smaller is faster
    folder="OrginalImages/"
    nameoffile="Blocks" #Stary Monster
    extension=".png" #jpg png
    Filename=folder+nameoffile+extension
    img=ResizeImage(Filename,reductepercntage)#Reduction in size # Percentage 20 is the current record
    # Applying a blur to the image doing this helps with high points
    ksize=1 # A Size object representing the size of the kernel. was 5 can go to 15 must be ODD
    sigmaX=ksize
    img = cv2.GaussianBlur(img,(ksize,sigmaX),0) #Gaussian Blur
    wantedwidth=20 # How wide
    wantedextrusion=3 #How tall
    ClassImg=ImagetoCad(img,wantedwidth,wantedextrusion)#(image, wantedwidth (mm), wantedextrusiion(mm))
    outputname="STL/"+str(nameoffile)+str(reductepercntage)+"Smooth"+str(ksize)+"List"+".stl"
    ClassImg.GiantAssembly.SaveMesh(outputname)
    print("File Ouputted: "+str(outputname))
    print("Finished the program in "+str(ProgramTimer.CheckTime())+" seconds\n")
        
    
if __name__ == "__main__":
    print("Starting")
    main()
    print("Finished!")


