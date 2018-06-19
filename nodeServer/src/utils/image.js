function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}


export class Image {
    
    constructor(data, pixHeight, pixWidth) {
	this.data = data
	this.pixHeight = pixHeight
	this.pixWidth = pixWidth
	this.scale = 1
	this.mask = []
	this.tempMask = []
	for (var i = 0; i < data.length; i++) {
	    this.mask.push([])
	    this.tempMask.push([])
	    for (var j = 0 ; j < data[0].length; j++) {
		this.mask[i].push(0)
		this.tempMask[i].push(0)
	    }
	}
    }

    drawImage(canvas, level, window, maskColours) {
	console.log("draw")
	// Get the dimensions
	var height = this.data.length
	var width  = this.data[0].length
	var pixHeight = this.pixHeight
	var pixWidth = this.pixWidth
	
	// Height of the canvas is always 400
	var size   = 400
	var actualSize = height*pixHeight
	
	// Size the canvas correctly
	var scale = size/actualSize
	this.scale = scale
	canvas.height = size
	canvas.width  = width * pixWidth * scale
	
	// Clear the canvas
	var ctx = canvas.getContext("2d")
	ctx.clearRect(0, 0, width*scale, height*scale);
	
	// Draw the image onto the canvas
	for (var row = 0; row < height; row++) {
	    for (var col = 0; col < width; col++) { 
		var grayVal = parseInt(this.data[row][col])
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
		ctx.fillStyle = rgbToHex(grayVal, grayVal, grayVal); // Set the color to the one specified
		ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(pixHeight*scale)); // Actually draw the rectangle

		// TEMP: colour the mask (could be an option?)
		if (this.mask[row][col] !== 0) {
		    ctx.fillStyle = "#FFFFFF"; // Set the color to the one specified
		    ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(pixHeight*scale));
		}

		let mask = this.tempMask
		if (row > 0 && mask[row][col] !== mask[row - 1][col]) {
		    if (mask[row][col] !== 0) {
			ctx.fillStyle = maskColours[mask[row][col] - 1]; // Set the color to the one specified
			ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(0.33*pixHeight*scale));
		    }
		    if (mask[row - 1][col] !== 0) {
			ctx.fillStyle = maskColours[mask[row - 1][col] - 1]; // Set the color to the one specified
			ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor((row-0.33) * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(0.33*pixHeight*scale));
		    }
		}
		if (col > 0 && mask[row][col] !== mask[row][col - 1]) {
		    if (mask[row][col] !== 0) {
			ctx.fillStyle = maskColours[mask[row][col] - 1]; // Set the color to the one specified
			ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(0.33*pixWidth*scale), Math.ceil(pixHeight*scale));
		    }
		    if (mask[row][col - 1] !== 0) {
			ctx.fillStyle = maskColours[mask[row][col - 1] - 1]; // Set the color to the one specified
			ctx.fillRect(Math.floor((col-0.33) * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(0.33*pixWidth*scale), Math.ceil(pixHeight*scale));
		    }
		}
	    }
	}
    }

    addToMask() {
	for (var row = 0; row < this.data.length; row++) {
	    for (var col = 0; col < this.data[0].length; col++) {	
		this.mask[row][col] = this.tempMask[row][col]
	    }
	}
    }

    updateTempMask(mouseX, mouseY, val, brushSize) {
	var y = -0.5 * this.pixHeight * this.scale
	for (var row = 0; row < this.data.length; row++) {
	    y += this.pixHeight * this.scale
	    var x = -0.5 * this.pixWidth * this.scale
	    for (var col = 0; col < this.data[0].length; col++) {	
		x += this.pixWidth * this.scale
		if ((x-mouseX)**2 + (y-mouseY)**2 < brushSize**2) {
		    this.tempMask[row][col] = val
		}
		else {
		    this.tempMask[row][col] = this.mask[row][col]
		}
	    }
	}
    }
}
