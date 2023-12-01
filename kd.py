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
        return median
        


    # Insert the Datum with the given code and coords into the tree.
    # The Datum with the given coords is guaranteed to not be in the tree.
    def insert(self,point:tuple[int],code:str):
        # print("inserting" + str(point))
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
        thisisaplaceholder = True

    # Find the k nearest neighbors to the point.
    def knn(self,k:int,point:tuple[int]) -> str:
        # Use the strategy discussed in class and in the notes.
        # The list should be a list of elements of type Datum.
        # While recursing, count the number of leaf nodes visited while you construct the list.
        # The following lines should be replaced by code that does the job.
        leaveschecked = 0
        knnlist = []
        # The following return line can probably be left alone unless you make changes in variable names.
        return(json.dumps({"leaveschecked":leaveschecked,"points":[datum.to_json() for datum in knnlist]},indent=2))