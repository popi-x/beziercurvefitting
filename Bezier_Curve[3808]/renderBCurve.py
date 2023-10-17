import numpy as np
import os,json,cv2,math
from components import readStrokes, get_bezier_parameters,bezier_curve,saveJson
from natsort import natsorted
import matplotlib.pyplot as plt

def renderSketch(strokes):
    canvas = np.ones((800,800),dtype="uint8")*255

    for stroke in strokes['strokes']:
        path = np.array(stroke['path']).astype("int")
        for i in range(len(path)-1):
            cv2.line(canvas,(path[i][0],path[i][1]),(path[i+1][0],path[i+1][1]),0,3)

    return canvas

def renderCurves(bezierPoints,srcStrokes):
    curves = []
    for i,curve in enumerate(bezierPoints):
        path = bezier_curve(curve,len(srcStrokes[i])).astype("int")
        curves.append({'path':path.tolist()})
    return {'strokes':curves}

def getValidStrokes(strokes,control_num):
    validStrokes = []
    for stroke in strokes['strokes']:
        if stroke['draw_type'] != 0 or len(stroke['path']) < control_num:
            continue
        path = np.array(stroke['path'])

        _, idx = np.unique(path,axis=0,return_index=True)

        if len(idx) > control_num:
            path = path[sorted(idx)]

        validStrokes.append(path)
    return validStrokes

def getStrokeBezier(control_num,srcStrokes):
    
    in_curves = []

    for i,src_p in enumerate(srcStrokes):
        if len(src_p) < control_num:
            continue
        src_p = np.array(src_p)
        inputs = get_bezier_parameters(src_p[:,0], src_p[:,1], degree=control_num-1)
        inputs = np.round(inputs).astype('int').flatten()/799
        
        in_curves.append(inputs)
    return np.array(in_curves)


json_path = r"C:\Users\ssinc\Desktop\CityU\fyp\beziercurve\Bezier_Curve[3808]\N001_0_0_MD_ccylinder.json"

## get stroke list
srcStrokes = readStrokes(json_path)

## remove the scaffold stroke and the stroke with less 6 points
validStrokes = getValidStrokes(srcStrokes,6)

## fit a bezier curve with 6 points for each stroke
b_curves = getStrokeBezier(6,validStrokes)

## render the fit curve
drawCurve = np.round(b_curves*799).astype('int')
drawCurve = renderCurves(drawCurve,validStrokes) ## sample points on each fit curve
fitSketch = renderSketch(drawCurve) ## render it to img

## compare the fit sketch with original one
srcSketch = renderSketch(srcStrokes)
plt.subplot(121)
plt.imshow(srcSketch)
plt.subplot(122)
plt.imshow(fitSketch)
plt.show()
