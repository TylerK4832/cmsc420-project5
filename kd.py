from __future__ import annotations
import json
import math
from typing import List

# Datum class.
# DO NOT MODIFY.
class Datum():
    def __init__(self,
                 coords : tuple[int],
                 code   : str):
        self.coords = coords
        self.code   = code
    def to_json(self) -> str:
        dict_repr = {'code':self.code,'coords':self.coords}
        return(dict_repr)


# Internal node class.
# DO NOT MODIFY.
class NodeInternal():
    def  __init__(self,
                  splitindex : int,
                  splitvalue : float,
                  leftchild,
                  rightchild):
        self.splitindex = splitindex
        self.splitvalue = splitvalue
        self.leftchild  = leftchild
        self.rightchild = rightchild

# Leaf node class.
# DO NOT MODIFY.
class NodeLeaf():
    def  __init__(self,
                  data : List[Datum]):
        self.data = data

# KD tree class.
class KDtree():
    def  __init__(self,
                  k    : int,
                  m    : int,
                  root = None):
        self.k    = k
        self.m    = m
        self.root = root

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    # DO NOT MODIFY.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            if isinstance(node,NodeLeaf):
                return {
                    "p": str([{'coords': datum.coords,'code': datum.code} for datum in node.data])
                }
            else:
                return {
                    "splitindex": node.splitindex,
                    "splitvalue": node.splitvalue,
                    "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                    "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
                }
        if self.root is None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)
    
    @staticmethod
    def maxSpread(data):
        if not data or not data[0]:
            return None

        k = len(data[0].coords)  # Assuming all tuples have the same length
        maxSpread = 0
        maxSpreadCoordinate = None
        minimum = None
        maximum = None
        for i in range(k):
            minimum = min(t.coords[i] for t in data)
            maximum= max(t.coords[i] for t in data)
            spread = maximum - minimum

            if spread > maxSpread:
                maxSpread = spread
                maxSpreadCoordinate = i

        return maxSpreadCoordinate
    
    @staticmethod
    def coordsMedian(data, coordinate):
        length = len(data)
        if length % 2 == 0:
            middle_left = data[length // 2 - 1].coords[coordinate]
            middle_right = data[length // 2].coords[coordinate]
            median = (middle_left + middle_right) / 2
        else:
            median = data[length // 2].coords[coordinate]
        return float(median)
        


    # Insert the Datum with the given code and coords into the tree.
    # The Datum with the given coords is guaranteed to not be in the tree.
    def insert(self,point:tuple[int],code:str):

        newEntry = Datum(point, code)

        if self.root == None:
            self.root = NodeLeaf([newEntry])
            return
        
        prevNode = None
        currNode = self.root
        while type(currNode) != NodeLeaf:
            prevNode = currNode
            if point[currNode.splitindex] < currNode.splitvalue:
                currNode = currNode.leftchild
            else:
                currNode = currNode.rightchild
        
        currNode.data.append(newEntry)

        # split if needed
        if len(currNode.data) > self.m:
            # print("splitting node with data " + str([{datum.coords} for datum in currNode.data]))
            coordinate = KDtree.maxSpread(currNode.data)
            # print("max spread coordinate (splitindex): " + str(coordinate))
            data = currNode.data
            sortedData = sorted(data, key=lambda x: x.coords[coordinate:] + x.coords[:coordinate])
            # print("sorted node data " + str([{datum.coords} for datum in sortedData]))
            median = math.floor((self.m + 1) / 2)
            splitvalue = KDtree.coordsMedian(sortedData, coordinate)
            # print("splitvalue: " + str(splitvalue))
            leftData = sortedData[:median]
            rightData = sortedData[median:]

            leftNode = NodeLeaf(leftData)
            rightNode = NodeLeaf(rightData)
            splitNode = NodeInternal(splitindex=coordinate, 
                                     splitvalue=splitvalue, 
                                     leftchild=leftNode, 
                                     rightchild=rightNode)
            if prevNode is None:
                self.root = splitNode
            elif currNode is prevNode.leftchild:
                prevNode.leftchild = splitNode
            else:
                prevNode.rightchild = splitNode


    # Delete the Datum with the given point from the tree.
    # The Datum with the given point is guaranteed to be in the tree.
    def delete(self,point:tuple[int]):
        if self.root == None: return
        
        parentNode = None
        grandNode = None
        currNode = self.root
        while type(currNode) != NodeLeaf:
            grandNode = parentNode
            parentNode = currNode
            if point[currNode.splitindex] < currNode.splitvalue:
                currNode = currNode.leftchild
            else:
                currNode = currNode.rightchild

        currNode.data = [d for d in currNode.data if d.coords != point]

        if not currNode.data:
            
            if parentNode is not None:

                if currNode is parentNode.leftchild:
                    sibling = parentNode.rightchild
                else:
                    sibling = parentNode.leftchild

                if grandNode is None:
                    self.root = sibling
                elif parentNode is grandNode.leftchild:
                    grandNode.leftchild = sibling
                else:
                    grandNode.rightchild = sibling

            else:
                self.root = None
    
    def distCoords(coord1:tuple[int], coord2:tuple[int]):
        squared_distance = sum((v1 - v2) ** 2 for v1, v2 in zip(coord1, coord2))
        distance = math.sqrt(squared_distance)
        return distance
    
    def getBB(root):
        if type(root) == NodeInternal:
            boxLeft = KDtree.getBB(root.leftchild)
            boxRight = KDtree.getBB(root.rightchild)
            box = tuple((min(t1[0], t2[0]), max(t1[1], t2[1])) for t1, t2 in zip(boxLeft, boxRight))
        elif type(root) == NodeLeaf:

            k = len(root.data[0].coords)

            minValues = [float('inf')] * k
            maxValues = [-float('inf')] * k

            for point in root.data:
                coords = point.coords
                for i in range(len(coords)):
                    minValues[i] = min(minValues[i], coords[i])
                    maxValues[i] = max(maxValues[i], coords[i])

            box = tuple((minVal, maxVal) for minVal, maxVal in zip(minValues, maxValues))
        return box
    
    def distBB(coord:tuple[int], box:tuple[tuple[int]]):
        sum = 0
        for interval, val in zip(box, coord):
            if val < interval[0]:
                sum = sum + (interval[0] - val) ** 2
            elif val > interval[1]:
                sum = sum + (val - interval[1]) ** 2
        return math.sqrt(sum)


    def knnhelper(root,leaveschecked,knnlist,k:int,point:tuple[int]) -> str:
        # Use the strategy discussed in class and in the notes.
        # The list should be a list of elements of type Datum.
        # While recursing, count the number of leaf nodes visited while you construct the list.
        # The following lines should be replaced by code that does the job.

        if type(root) == NodeInternal:

            if knnlist:
                distFurthest = KDtree.distCoords(point,knnlist[-1].coords)
            else:
                distFurthest = float('inf')

            boxLeft = KDtree.getBB(root.leftchild)
            distLeft = KDtree.distBB(point,boxLeft)
            boxRight = KDtree.getBB(root.rightchild)
            distRight = KDtree.distBB(point,boxRight)

            if distLeft <= distRight and (len(knnlist) < k or distLeft < distFurthest):
                (leaveschecked, knnlist) = KDtree.knnhelper(root.leftchild,leaveschecked,knnlist,k,point)
                distFurthest = KDtree.distCoords(point,knnlist[-1].coords)
                if len(knnlist) < k or distRight < distFurthest:
                    (leaveschecked, knnlist) = KDtree.knnhelper(root.rightchild,leaveschecked,knnlist,k,point)
            elif distRight < distLeft and (len(knnlist) < k or distRight < distFurthest):
                (leaveschecked, knnlist) = KDtree.knnhelper(root.rightchild,leaveschecked,knnlist,k,point)
                distFurthest = KDtree.distCoords(point,knnlist[-1].coords)
                if len(knnlist) < k or distLeft < distFurthest:
                    (leaveschecked, knnlist) = KDtree.knnhelper(root.leftchild,leaveschecked,knnlist,k,point)

            return (leaveschecked, knnlist)

        elif type(root) == NodeLeaf:

            newknnlist = root.data + knnlist
            newknnlist = sorted(newknnlist, key=lambda p: KDtree.distCoords(p.coords,point))
            newknnlist = newknnlist[:min(k,len(newknnlist))]
        
            return (leaveschecked + 1, newknnlist)
    

    # Find the k nearest neighbors to the point.
    def knn(self,k:int,point:tuple[int]) -> str:

        (leaveschecked, knnlist) = KDtree.knnhelper(self.root,0,[],k,point)

        return(json.dumps({"leaveschecked":leaveschecked,"points":[datum.to_json() for datum in knnlist]},indent=2))