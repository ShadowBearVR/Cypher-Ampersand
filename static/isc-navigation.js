class Path {
    constructor(id, start, end) {
      this.id = id;
      this.start = start;
      this.end = end;
      this.neighbors = new Set();
      this.rooms = new Set();
    }
    
    addNeighbor(neighborPath) {
      this.neighbors.add(neighborPath);
    }

    addRoom(room) {
        this.rooms.add(room);
      }
}

function setStartingPoint(roomID) {
    document.getElementById(roomID).classList.add("starting-room");
    document.getElementById(roomConnectors[roomID]).classList.add("starting-path");
}

function setEndingPoint(roomID) {
    document.getElementById(roomID).classList.add("ending-room");
    document.getElementById(roomConnectors[roomID]).classList.add("ending-path");
}

traversalPath = []

function computePaths() {
    console.log("traversing from " + startingPathID + " " + endingPathID);
    var output = findShortestPath(pathDict[startingPathID], pathDict[endingPathID], pathDict);
    console.log(output);

    colorTraversalPath(false);
    traversalPath = [];

    while(output.length > 0) {
        path = output.shift();
        traversalPath.push(path);
        console.log("Path is " + path.id);
    }
    console.log(traversalPath);
    colorTraversalPath(true);

}

function colorTraversalPath(highlighted) {
    for(let i = 0; i < traversalPath.length; i++) {
        path = traversalPath[i];
        if(highlighted) {
            document.getElementById(path.id).classList.add('highlight-path');
        } else {
            document.getElementById(path.id).classList.remove('highlight-path');
        }
    }
}

function findShortestPath(startPath, endPath, paths) {
    const visited = new Set();
    const queue = [[startPath, []]]; // Queue of paths and their corresponding history of paths taken to get there
    while (queue.length > 0) {
      const [currentPath, pathHistory] = queue.shift();
      console.log(currentPath);
      if (currentPath === endPath) {
        return pathHistory.concat(currentPath); // Return the shortest path
      }
      visited.add(currentPath); // Mark the current path as visited
      for (const neighborID of currentPath.neighbors) { // Iterate over the neighbors of the current path
        neighbor = paths[neighborID];
        if (!visited.has(neighbor)) { // If the neighbor has not been visited yet
          queue.push([neighbor, pathHistory.concat(currentPath)]); // Add the neighbor to the queue with its path history
        }
      }
    }
    return null; // If there is no path between the start and end paths, return null
  
}









var pathDict = {}
var roomConnectors = {}







function createNeighborList() {
    var text = " "
    var pathGroup = document.getElementById('Paths')
    var paths = pathGroup.children

    //var roomGroup = document.getElementById('RoomPoints');
    //var rooms = roomGroup.children;

    for (let i = 0; i < paths.length; i++) {
        let thisPath = new Path(paths[i].id, [paths[i].x1.baseVal.value, paths[i].y1.baseVal.value], [paths[i].x2.baseVal.value, paths[i].y2.baseVal.value])
        pathDict[paths[i].id] = thisPath

        for(let j = 0; j < paths.length; j++) {
            if(paths[i] == paths[j]) {
                continue;     
			}
            
            let otherPath = new Path(paths[j].id, [paths[j].x1.baseVal.value, paths[j].y1.baseVal.value], [paths[j].x2.baseVal.value, paths[j].y2.baseVal.value]);
            
            var neighbor = false;

            if(compareDistance(thisPath.start, otherPath.start)) {
                neighbor = true;
			}
            if(compareDistance(thisPath.end, otherPath.start)) {
                neighbor = true;  
			}
            if(compareDistance(thisPath.start, otherPath.end)) {
                neighbor = true;
			}
            if(compareDistance(thisPath.end, otherPath.end)) {
                neighbor = true;
			}

            if(neighbor == true) {
                thisPath.addNeighbor(otherPath.id);   
            }
		}

        /*for (let k = 0; k < rooms.length; k++) {
              var roomCoords = [rooms[k].cx.baseVal.value, rooms[k].cy.baseVal.value];
              if(compareDistance(thisPath.start, roomCoords) || compareDistance(thisPath.end, roomCoords)) {
                pathDict[paths[i].id].addRoom(rooms[k].id);
                roomConnectors[rooms[k].id] = paths[i].id;
                
			  }
		}*/
    }

    console.log(pathDict)
}












function compareDistance(coords1, coords2) {
    const threshold = 1;
    if(Math.abs(coords1[0]-coords2[0]) < threshold) {
        if(Math.abs(coords1[1]-coords2[1]) < threshold) {
            return true
        }
    }
    return false
}












function colorPath(pathID) {
    var path = document.getElementById(pathID);
    document.getElementById("debug").innerHTML = path;
    path.classList.add("trav");
    highlightNeighbor(pathID, true);
    highlightRooms(pathID, true);
}

function highlightNeighbor(pathID, active) {
    for(let neighbor of pathDict[pathID].neighbors) {
        var path = document.getElementById(neighbor);
        if(active) {
            path.classList.add("neighbor");
        } else {
            path.classList.remove("neighbor");
		}
	}
}

function highlightRooms(pathID, active) {
    for(let room of pathDict[pathID].rooms) {
        var path = document.getElementById(room);
        if(active) {
            path.classList.add("neighbor-room");
        } else {
            path.classList.remove("neighbor-room");
		}
	}
}



function mouseOver(pathObj) {
    //startingPathID = pathObj.id;
    //document.getElementById('path-name').firstChild.data = pathObj.id;
    //colorPath(pathObj.id);
}

function mouseOut(pathObj) {
    //startingPathID = null;
    //document.getElementById('path-name').firstChild.data = "blank";
    //document.getElementById(pathObj.id).classList.remove("trav");
    //highlightNeighbor(pathObj.id, false);
    //highlightRooms(pathObj.id, false);
}

lastPickedStarting = false;
var endingPathID = null;
startingPathID = null;

function mouseDown(element) {
    if(lastPickedStarting == true) {
        if(endingPathID) {
            document.getElementById(endingPathID).classList.remove("ending-path");
            endingPathID = null;
        }
        
        endingPathID = element.id;
        document.getElementById(endingPathID).classList.add("ending-path");
        console.log("Set ending path to " + endingPathID);
        console.log("Starting path is " + startingPathID);
    } else {
        if(startingPathID) {
            document.getElementById(startingPathID).classList.remove("starting-path");
            startingPathID = null;
        }
        
        startingPathID = element.id;
        document.getElementById(startingPathID).classList.add("starting-path");
        console.log("Set starting path to " + startingPathID);
        console.log("Ending path is " + endingPathID);
    }
    if(startingPathID && endingPathID && startingPathID != endingPathID) {
        computePaths();
    }
    lastPickedStarting = !lastPickedStarting;
}

window.onload = function() {
  createNeighborList();
  //setStartingPoint("room1");
};