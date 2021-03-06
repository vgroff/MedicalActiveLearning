function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

// Image for the logic of a 2D image
export class Image {
    
    constructor(data, pixHeight, pixWidth) {
	this.data = data
	this.pixHeight = pixHeight
	this.pixWidth = pixWidth
	this.scale = 1
	this.mask = []
	this.tempMask = []
	for (var i = 0; i < data.length; i++) {
	    var mask = []
	    var tempMask = []
	    for (var j = 0 ; j < data[0].length; j++) {
		mask.push(0)
		tempMask.push(0)
	    }
	    this.mask.push(new Uint8Array(mask))
	    this.tempMask.push(new Uint8Array(tempMask))
	}
	this.masks = [this.mask]
	this.currentMask = 0
	this.boundingRect = [0,0,0,0]
	this.boundingRectPix = [0,0,0,0]
	this.events = {"rectChange":[], "maskChange":[]}
	this.preRender = null
	this.preRenderLevel = null
	this.preRenderWindow = null
    }

    // Draw the image on the canvas
    drawImage(canvas, canvasSize, level, window, maskVisibility, maskColours) {
	//console.log("draw", level, window)
	// Get the dimensions
	var height = this.data.length
	var width  = this.data[0].length
	var pixHeight = this.pixHeight
	var pixWidth = this.pixWidth
	
	var size   = canvasSize
	if (height > width) {
	    // Calculate unscaled height
	    var actualSize = height*pixHeight
	    
	    // Size the canvas correctly
	    var scale = size/actualSize
	    this.scale = scale
	    canvas.height = size
	    canvas.width  = width * pixWidth * scale
	}
	else {
	    // Calc unscaled  width
	    var actualSize = width*pixWidth
	    // Size canvas
	    var scale = size/actualSize
	    this.scale = scale
	    canvas.width  = size
	    canvas.height = height*pixHeight*scale
	}

	// Clear the canvas
	var ctx = canvas.getContext("2d")
	ctx.clearRect(0, 0, width*scale, height*scale);
	// Draw the image
	if (this.preRender !== null && this.preRenderLevel === level
	    && this.preRenderWindow === window) {
	    ctx.drawImage(this.preRender, 0, 0)
	}
	else {
	    this.drawImageOnly(canvas, canvasSize, level, window, maskVisibility, maskColours)
	}
	// Draw the image onto the canvas
	for (var row = 0; row < height; row++) {
	    for (var col = 0; col < width; col++) { 
		for (var i = 0; i < this.masks.length; i++) {
		    if (maskVisibility[i] === false) {
			continue
		    }
		    if (this.currentMask === i) {
			var mask = this.tempMask
		    }
		    else {
			var mask = this.masks[i]
		    }
		    if (row > 0 && mask[row][col] !== mask[row - 1][col]) {
			if (mask[row][col] !== 0) {
			    // Set the color to the one specified
			    ctx.fillStyle = maskColours[i][mask[row][col] - 1]; 
			    ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(0.33*pixHeight*scale));
			}

			if (mask[row - 1][col] !== 0) {
			    ctx.fillStyle = maskColours[i][mask[row - 1][col] - 1];
			    ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor((row-0.33) * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(0.33*pixHeight*scale));
			}
		    }

		    if (col > 0 && mask[row][col] !== mask[row][col - 1]) {
			if (mask[row][col] !== 0) {
			    ctx.fillStyle = maskColours[i][mask[row][col] - 1]; 
			    ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(0.33*pixWidth*scale), Math.ceil(pixHeight*scale));
			}
			if (mask[row][col - 1] !== 0) {
			    ctx.fillStyle = maskColours[i][mask[row][col - 1] - 1]; 
			    ctx.fillRect(Math.floor((col-0.33) * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(0.33*pixWidth*scale), Math.ceil(pixHeight*scale));
			}
		    }
		}
	    }
	}
	this.boundingRect[1] = this.rowToCoord(this.boundingRectPix[1])
	this.boundingRect[3] = this.rowToCoord(this.boundingRectPix[3])
	this.boundingRect[0] = this.colToCoord(this.boundingRectPix[0])
	this.boundingRect[2] = this.colToCoord(this.boundingRectPix[2])
	ctx.beginPath();
	ctx.rect(this.boundingRect[0],
		 this.boundingRect[1],
		 this.boundingRect[2] - this.boundingRect[0],// * (pixWidth * scale),
		 this.boundingRect[3] - this.boundingRect[1])
	ctx.lineWidth = 3
	ctx.strokeStyle = 'yellow';
	ctx.stroke()
    }

    drawImageOnly(canvas, canvasSize, level, window) {
	// Get the dimensions
	var height = this.data.length
	var width  = this.data[0].length
	var pixHeight = this.pixHeight
	var pixWidth = this.pixWidth

	var size   = canvasSize
	if (height > width) {
	    // Calculate unscaled height
	    var actualSize = height*pixHeight
	    
	    // Size the canvas correctly
	    var scale = size/actualSize
	    this.scale = scale
	    canvas.height = size
	    canvas.width  = width * pixWidth * scale
	}
	else {
	    // Calc unscaled  width
	    var actualSize = width*pixWidth
	    // Size canvas
	    var scale = size/actualSize
	    this.scale = scale
	    canvas.width  = size
	    canvas.height = height*pixHeight*scale
	}
	// Clear the canvas
	var ctx = canvas.getContext("2d")
	ctx.clearRect(0, 0, width*scale, height*scale);
	// Draw the image onto the canvas
	for (var row = 0; row < height; row++) {
	    for (var col = 0; col < width; col++) { 
		var grayVal = (this.data[row][col])
		var oldGray = grayVal
		// Transfer function
		if (grayVal < level - window/2) {
		    grayVal = 0
		}
		else if (grayVal > level + window/2) {
		    grayVal = 255
		}
		else {
		    grayVal = (grayVal - (level - window/2))*255/window
		}
		grayVal = Math.round(grayVal)
		//if (grayVal < 0 || grayVal > 255) {
		//    console.log("GRAY", grayVal > level + window/2, oldGray, grayVal, level, window)
		//}

		ctx.fillStyle = rgbToHex(grayVal, grayVal, grayVal); // Set the color to the one specified
		if (ctx.fillStyle == "#NaN#NaN#NaN") {
		    console.log(oldGray, grayVal)
		}
		ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(pixHeight*scale)); // Actually draw the rectangle
		
	    }
	}
    }

    // Pre render the images
    preRenderImage(canvasSize, level, window) {
	var canvas = document.createElement("canvas")
	this.drawImageOnly(canvas, canvasSize, level, window)
	this.preRender = canvas
	this.preRenderLevel = level
	this.preRenderWindow = window
    }

    // Reset the temporary mask to the permanent mask
    resetTempMask() {
	for (var row = 0; row < this.data.length; row++) {
	    for (var col = 0; col < this.data[0].length; col++) {
		if (this.mask[row][col] !== this.tempMask[row][col]) { 
		    this.tempMask[row][col] = this.mask[row][col]
		}
	    }
	}
    }

    addNewMask(mask) {
	var mask = []
	for (var i = 0; i < this.data.length; i++) {
	    var temp = []
	    for (var j = 0 ; j < this.data[0].length; j++) {
		temp.push(0)
	    }
	    mask.push(new Uint8Array(temp))
	    
	}
	this.masks.push(mask)
    }

    setActiveMask(n) {
	this.mask = this.masks[n]
	this.currentMask = n
	this.resetTempMask()
    }

    // Convert temporary mask to permanent
    addToMask() {
	for (var row = 0; row < this.data.length; row++) {
	    for (var col = 0; col < this.data[0].length; col++) {
		if (this.mask[row][col] !== this.tempMask[row][col]) { 
		    this.mask[row][col] = this.tempMask[row][col]
		    for (var i = 0; i < this.events.maskChange.length; i++) {
			this.events.maskChange[i](row, col, this.mask[row][col], this.currentMask)
		    }
		}
	    }
	}
    }

    // Update the temporary mask depending on the brush
    updateTempMask(mouseX, mouseY, val, brushSize) {
	// set mouseX/Y to middle of pixel
	mouseY = (Math.floor(mouseY/(this.pixHeight*this.scale))+0.5)*this.pixHeight*this.scale
	mouseX = (Math.floor(mouseX/(this.pixWidth*this.scale))+0.5)*this.pixWidth*this.scale
	var largestDist = 0.25 * (Math.ceil(this.pixHeight*this.scale)**2 + Math.ceil(this.pixWidth*this.scale)**2)
	var brushSizeSq = brushSize*largestDist 
	var stats = []
	var y = -0.5 * this.pixHeight * this.scale
	for (var row = 0; row < this.data.length; row++) {
	    y += this.pixHeight * this.scale
	    var x = -0.5 * this.pixWidth * this.scale
	    for (var col = 0; col < this.data[0].length; col++) {	
		x += this.pixWidth * this.scale
		if ((x-mouseX)**2 + (y-mouseY)**2 < brushSizeSq) {
		    this.tempMask[row][col] = val
		}

		else {
		    this.tempMask[row][col] = this.mask[row][col]
		}
	    }
	}
    }

    // Set the ending coordinates of the rectangle
    setRectEndCoords(x, y, width, height) {
	let colX = this.coordToColX(x)
	let rowY = this.coordToRowY(y)
	this.boundingRect[2] = colX
	this.boundingRect[3] = rowY
	let col = this.coordToCol(x)
	let row = this.coordToRow(y)
	this.boundingRectPix[2] = col
	this.boundingRectPix[3] = row
	for (var i = 0; i < this.events.rectChange.length; i++) {
	    this.events.rectChange[i](this.boundingRectPix)
	}
    }

    setRectStartCoords(x,y) {
	this.boundingRect[0] = this.coordToColX(x)
	this.boundingRect[1] = this.coordToRowY(y)
	let col = this.coordToCol(x)
	let row = this.coordToRow(y)
	this.boundingRectPix[0] = col
	this.boundingRectPix[1] = row
    }

    setRectPix(row1, col1, row2, col2) {
	this.boundingRectPix[1] = row1
	this.boundingRectPix[0] = col1
	this.boundingRectPix[3] = row2
	this.boundingRectPix[2] = col2
	this.boundingRect[1] = this.rowToCoord(row1)
	this.boundingRect[3] = this.rowToCoord(row2)
	this.boundingRect[0] = this.colToCoord(col1)
	this.boundingRect[2] = this.colToCoord(col2)
    }

    setRectCoords(x1, y1, x2, y2) {
	this.boundingRect[0] = x1
	this.boundingRect[2] = x2
	this.boundingRect[1] = y1
	this.boundingRect[3] = y2
	this.boundingRectPix[1] = Math.round(y1/(this.pixHeight*this.scale))
	this.boundingRectPix[0] = Math.round(x1/(this.pixWidth*this.scale))
	this.boundingRectPix[3] = Math.round(y2/(this.pixHeight*this.scale))
	this.boundingRectPix[2] = Math.round(x2/(this.pixWidth*this.scale))
	for (var i = 0; i < this.events.rectChange.length; i++) {
	    this.events.rectChange[i](this.boundingRectPix)
	}
    }

    addEvent(type, f) {
	this.events[type].push(f)
    }

    colToCoord(x) {
	return x*this.pixWidth*this.scale
    }

    rowToCoord(y) {
	return y*this.pixHeight*this.scale
    }

    coordToCol(x) {
	return Math.floor(x/(this.pixWidth*this.scale))
    }

    coordToRow(y) {
	return Math.floor(y/(this.pixHeight*this.scale))
    }

    coordToColX(x) {
	return this.colToCoord(this.coordToCol(x))
    }

    coordToRowY(y) {
	return this.rowToCoord(this.coordToRow(y))
    }
}



// Have an add new mask option, have the first mask in a list of masks and have an "active mask" index that starts on 0 but can be changed. Send the mask index up with maskChange event
